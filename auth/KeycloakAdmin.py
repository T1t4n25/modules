"""Responsible for all admin functions like user Management"""

import asyncio
import aiohttp
import logging
import uuid
from typing import Optional
from async_lru import alru_cache

# Local imports
from auth.KeycloakConfig import KeycloakConfig
from utility.exc.BusinessException import BusinessException
from utility.localization.messages.Errors import (
    AUTH_SERVER_UNAVAILABLE,
    AUTH_TOKEN_EXPIRED,
    USER_NOT_FOUND,
    UNEXPECTED_ERROR,
    ROLE_REVOCATION_FAILED
)

class KeycloakAdmin:
    _instance: Optional['KeycloakAdmin'] = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(KeycloakAdmin, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, main_logger: logging.Logger = None, config: KeycloakConfig = KeycloakConfig()):
        if not hasattr(self, '_initialized'):
            self.config = config
            self.max_retries = 3
            self.retry_delay = 1  # seconds
            self._initialized = True
            
        # Initialize logger
        if main_logger:
            self.logger = logging.getLogger(f"{main_logger.name}.KeycloakAdmin")
            self.logger.setLevel(main_logger.level)
        else:
            self.logger = logging.getLogger("KeycloakAdmin")
            self.logger.setLevel(logging.INFO)
            

    @alru_cache(maxsize=1)
    async def _get_admin_token(self) -> str:
        """
        Obtain an access token for the Keycloak admin client using client credentials.
        Uses LRU cache to avoid unnecessary token requests.

        Returns:
            str: The admin access token.
        """
        token_url: str = self.config.token_url
        data: dict = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=data) as response:
                response.raise_for_status()
                token_data = await response.json()
                return token_data["access_token"]

    def _clear_token_cache(self):
        """
        Clear the cached token to force a new token request.
        """
        self._get_admin_token.cache_clear()

    async def _make_request_with_retry(self, method: str, url: str, **kwargs) -> dict:
        """
        Make an HTTP request with retry mechanism for connection failures and token invalidation.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE).
            url (str): The URL to make the request to.
            **kwargs: Additional arguments to pass to aiohttp.
            
        Returns:
            dict: Response data and status code.
            
        Raises:
            BusinessException: If all retries are exhausted or specific errors occur.
        """
        
        for attempt in range(self.max_retries):
            try:
                # Ensure we have headers with a fresh token for each attempt
                if 'headers' not in kwargs:
                    kwargs['headers'] = await self._headers()
                else:
                    # Update the token in existing headers
                    kwargs['headers']['Authorization'] = f"Bearer {await self._get_admin_token()}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.request(method, url, **kwargs) as response:
                        response.raise_for_status()
                        data = await response.json() if response.content_type == 'application/json' else None
                        return {
                            'status': response.status,
                            'data': data,
                            'response': response
                        }
                
            except aiohttp.ClientResponseError as e:
                # Log the error for developers
                self.logger.error(f"Keycloak API error: {method} {url} - Status: {e.status}, Message: {e.message}")
                
                # Handle token invalidation (401/403) by clearing cache and retrying
                if e.status in [401, 403]:
                    if attempt < self.max_retries - 1:
                        # Clear token cache and retry with fresh token
                        self.logger.warning(f"Token expired, clearing cache and retrying. Attempt {attempt + 1}/{self.max_retries}")
                        self._clear_token_cache()
                        continue
                    else:
                        # Last attempt failed, raise BusinessException
                        self.logger.error("Token refresh failed after all retries")
                        raise BusinessException(AUTH_TOKEN_EXPIRED)
                elif e.status == 404:
                    # Not found errors - log for developers, show generic error to users
                    self.logger.error(f"Resource not found: {method} {url}")
                    if 'user' in url.lower():
                        raise BusinessException(USER_NOT_FOUND)
                    else:
                        # For other 404s, log the specific error but show generic message
                        self.logger.error(f"Keycloak resource not found: {url}")
                        raise BusinessException(UNEXPECTED_ERROR)
                elif e.status >= 500:
                    # Server errors - log for developers, show server unavailable to users
                    self.logger.error(f"Keycloak server error: {e.status} - {e.message}")
                    raise BusinessException(AUTH_SERVER_UNAVAILABLE)
                else:
                    # Other client errors - log for developers
                    self.logger.error(f"Keycloak client error: {e.status} - {e.message}")
                    raise BusinessException(UNEXPECTED_ERROR)
                    
            except (aiohttp.ClientConnectionError, aiohttp.ClientTimeout) as e:
                self.logger.warning(f"Connection error (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    break
            except aiohttp.ClientError as e:
                # Other aiohttp errors - log for developers
                self.logger.error(f"Keycloak connection error: {str(e)}")
                raise BusinessException(AUTH_SERVER_UNAVAILABLE)
        
        # If we get here, all retries failed
        self.logger.error(f"All retry attempts failed for {method} {url}")
        raise BusinessException(AUTH_SERVER_UNAVAILABLE)

    async def _headers(self) -> dict:
        """
        Construct the authorization and content-type headers for Keycloak requests.

        Returns:
            dict: Headers including the bearer token and content type.
        """
        return {
            "Authorization": f"Bearer {await self._get_admin_token()}",
            "Content-Type": "application/json"
        }

    async def add_user_uuidv7_attribute(self, user_id: str, uuidv7: str) -> bool:
        """
        Add or update the 'our_uuidv7' attribute for a specific Keycloak user.

        Args:
            user_id (str): The Keycloak user ID.
            uuidv7 (str): The UUIDv7 value to set in the user's attributes.

        Returns:
            bool: True if the attribute was updated successfully, False otherwise.
            
        Raises:
            BusinessException: If user not found or update fails.
        """
        try:
            self.logger.info(f"Updating user {user_id} with uuidv7: {uuidv7}")
            user_url: str = self.config.user_url(user_id=user_id)
            resp = await self._make_request_with_retry('GET', user_url)
            user = resp['data']
            attributes = user.get('attributes', {})
            attributes['our_uuidv7'] = [uuidv7]
            # Only use payload for updated attributes, avoid sending any field that shouldn't change
            user["attributes"] = attributes

            put_resp = await self._make_request_with_retry('PUT', user_url, json=user)
            if put_resp['status'] != 204:
                self.logger.error(f"Failed to update user {user_id}: HTTP {put_resp['status']}")
                raise BusinessException(UNEXPECTED_ERROR)
            
            self.logger.info(f"Successfully updated user {user_id} with uuidv7: {uuidv7}")
            return True
        except BusinessException:
            raise
        except Exception as e:
            error_id = str(uuid.uuid1())
            self.logger.exception(f"[{error_id}]Unexpected error updating user {user_id}: {str(e)}")
            raise BusinessException(UNEXPECTED_ERROR, error_id=error_id)

    async def update_user_info(self, user_id: str, first_name: str = None, last_name: str = None, email: str = None, phone_number: str = None) -> bool:
        """
        Update user's info (first name, last name, email, phone number) in Keycloak.

        Args:
            user_id (str): The Keycloak user ID.
            first_name (str, optional): New first name.
            last_name (str, optional): New last name.
            email (str, optional): New email.
            phone_number (str, optional): New phone number.

        Returns:
            bool: True if update successful, False otherwise.

        Raises:
            BusinessException: If user not found or update fails.
        """
        try:
            self.logger.info(f"Updating user info for user {user_id}")
            user_url: str = self.config.user_url(user_id)
            resp = await self._make_request_with_retry('GET', user_url)
            user = resp['data']

            # Prepare update payload
            payload = {}

            if first_name is not None:
                payload["firstName"] = first_name
            if last_name is not None:
                payload["lastName"] = last_name
            if email is not None:
                payload["email"] = email

            # Keycloak custom attribute for phone number
            attributes = user.get('attributes', {})
            if phone_number is not None:
                attributes['phone_number'] = [phone_number]
                payload["attributes"] = attributes
            elif attributes:
                payload["attributes"] = attributes

            if not payload:
                self.logger.warning(f"No update fields provided for user {user_id}")
                return True  # Nothing to update

            put_resp = await self._make_request_with_retry('PUT', user_url, json=payload)
            if put_resp['status'] != 204:
                self.logger.error(f"Failed to update user {user_id}: HTTP {put_resp['status']}")
                raise BusinessException(UNEXPECTED_ERROR)

            self.logger.info(f"Successfully updated user {user_id} info in Keycloak.")
            return True

        except BusinessException:
            raise
        except Exception as e:
            error_id = str(uuid.uuid1())
            self.logger.exception(f"[{error_id}]Unexpected error updating user info for {user_id}: {str(e)}")
            raise BusinessException(UNEXPECTED_ERROR, error_id=error_id)

    async def assign_role_to_user(self, user_id: str, role_name: str, client_id: str = None) -> bool:
        """
        Assign a realm-level or client-level role to a user.

        Args:
            user_id (str): The Keycloak user ID.
            role_name (str): The name of the role to assign.
            client_id (str, optional): The client ID for client-level roles. If None, assigns a realm-level role.

        Returns:
            bool: True if the role was assigned successfully, False otherwise.
            
        Raises:
            BusinessException: If role not found or assignment fails.
        """
        try:
            role_type = "realm-level" if client_id is None else f"client-level (client: {client_id})"
            self.logger.info(f"Assigning {role_type} role '{role_name}' to user {user_id}")
            
            if client_id is None:
                # Realm-level role
                role_url = self.config.realm_role_url(role_name)
                mapping_url = self.config.realm_role_mapping_url(user_id)
            else:
                # Client-level role
                role_url = self.config.client_role_detail_url(client_id, role_name)
                mapping_url = self.config.client_role_mapping_url(user_id, client_id)

            # Get the Role dict
            role_resp = await self._make_request_with_retry('GET', role_url)
            role = role_resp['data']

            # Assign Role
            role_assign_resp = await self._make_request_with_retry('POST', mapping_url, json=[role])
            if role_assign_resp['status'] not in (200, 204):
                self.logger.error(f"Failed to assign role '{role_name}' to user {user_id}: HTTP {role_assign_resp['status']}")
                raise BusinessException(UNEXPECTED_ERROR)
            
            self.logger.info(f"Successfully assigned role '{role_name}' to user {user_id}")
            return True
        except BusinessException:
            raise
        except Exception as e:
            error_id = str(uuid.uuid1())
            self.logger.exception(f"[{error_id}]Unexpected error assigning role '{role_name}' to user {user_id}: {str(e)}")
            raise BusinessException(UNEXPECTED_ERROR, error_id=error_id)

    async def revoke_role_from_user(self, user_id: str, role_id: int, client_id: str = None) -> bool:
        """
        Revoke a realm-level or client-level role from a user.

        Args:
            user_id (str): The Keycloak user ID.
            role_id (int): The ID of the role to revoke.
            client_id (str, optional): The client ID for client-level roles. If None, revokes a realm-level role.

        Returns:
            bool: True if the role was revoked successfully, False otherwise.
            
        Raises:
            BusinessException: If role not found or revocation fails.
        """
        try:
            role_type = "realm-level" if client_id is None else f"client-level (client: {client_id})"
            self.logger.info(f"Revoking {role_type} role '{role_id}' from user {user_id}")

            # Revoke Role
            role_revoke_resp = await self._make_request_with_retry('DELETE', self.config.client_role_mapping_url(user_id, client_id), json=[role_id])
            if role_revoke_resp['status'] not in (200, 204):
                self.logger.error(f"Failed to revoke role '{role_id}' from user {user_id}: HTTP {role_revoke_resp['status']}")
                raise BusinessException(ROLE_REVOCATION_FAILED)
            else:
                self.logger.info(f"Successfully revoked role '{role_id}' from user {user_id}")
                return True
        except BusinessException:
            raise
        except Exception as e:
            error_id = str(uuid.uuid1())
            self.logger.exception(f"[{error_id}]Unexpected error revoking role '{role_id}' from user {user_id}: {str(e)}")
            raise BusinessException(UNEXPECTED_ERROR, error_id=error_id)

    async def delete_user_from_keycloak(self, user_id: str) -> bool:
        """
        Delete a user from Keycloak.

        Args:
            user_id (str): The Keycloak user ID.

        Returns:
            bool: True if the user was deleted successfully, False otherwise.
            
        Raises:
            BusinessException: If user not found or deletion fails.
        """
        try:
            self.logger.info(f"Deleting user {user_id} from Keycloak")
            user_url: str = self.config.user_url(user_id=user_id)
            
            delete_resp = await self._make_request_with_retry('DELETE', user_url)
            if delete_resp['status'] not in (200, 204):
                self.logger.error(f"Failed to delete user {user_id} from Keycloak: HTTP {delete_resp['status']}")
                raise BusinessException(UNEXPECTED_ERROR)
            
            self.logger.info(f"Successfully deleted user {user_id} from Keycloak")
            return True
        except BusinessException:
            raise
        except Exception as e:
            error_id = str(uuid.uuid1())
            self.logger.exception(f"[{error_id}]Unexpected error deleting user {user_id} from Keycloak: {str(e)}")
            raise BusinessException(UNEXPECTED_ERROR, error_id=error_id)

    async def add_role(self, role_name: str, description: str = "", client_id: str = None) -> bool:
        """
        Add a realm-level or client-level role in Keycloak.

        Args:
            role_name (str): The name of the role to add.
            description (str, optional): A description for the role.
            client_id (str, optional): The client ID for client roles. If None, adds a realm-level role.

        Returns:
            bool: True if the role was added successfully, False otherwise.
            
        Raises:
            BusinessException: If role creation fails.
        """
        try:
            role_type = "realm-level" if client_id is None else f"client-level (client: {client_id})"
            self.logger.info(f"Creating {role_type} role '{role_name}' with description: '{description}'")
            
            payload = {
                "name": role_name,
                "description": description,
                "composite": False
            }
            if client_id is None:
                # Add realm role
                roles_url = self.config.realm_roles_url
            else:
                # Add client role
                roles_url = self.config.client_roles_url(client_id)

            resp = await self._make_request_with_retry('POST', roles_url, json=payload)
            if resp['status'] not in (201, 204):
                self.logger.error(f"Failed to create role '{role_name}': HTTP {resp['status']}")
                raise BusinessException(UNEXPECTED_ERROR)
            
            self.logger.info(f"Successfully created role '{role_name}'")
            return True
        except BusinessException:
            raise
        except Exception as e:
            error_id = str(uuid.uuid1())
            self.logger.exception(f"[{error_id}]Unexpected error creating role '{role_name}': {str(e)}")
            raise BusinessException(UNEXPECTED_ERROR, error_id=error_id)

