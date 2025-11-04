'''
Handles verification of JWT tokens
'''
# from pathlib import Path
# import sys
# sys.path.append(str(Path(__file__).resolve().parent.parent))

import jwt
from async_lru import alru_cache
import aiohttp
from typing import Dict, Any
from logging import Logger, getLogger
import uuid

# Local imports
from auth import KeycloakConfig
from auth.Exceptions import AuthException
from utility.localization.messages import AUTH_SERVER_UNAVAILABLE, AUTH_TOKEN_EXPIRED, AUTH_FORBIDDEN, AUTH_INVALID_SESSION, UNEXPECTED_ERROR, AUTH_INVALID_AUDIENCE

class KeycloakJWTHandler:
    """Handles verification of JWT tokens"""
    def __init__(self, config: KeycloakConfig = KeycloakConfig(), logger: Logger = getLogger("__main__")):
        self.config = config
        self._public_keys = None
        self._last_keys_fetch = 0
        self.logger = getLogger(f"{logger.name}.KeycloakJWTHandler")
        self.logger.setLevel(logger.level) 
        
    @alru_cache(maxsize=1)  # Cache the public keys preventing frequent network calls
    async def __get_public_keys(self) -> Dict[str, Any]:
        """Fetch and cache Keycloak public keys"""
        try:
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.config.jwks_url, timeout=10) as response:
                    response.raise_for_status()
                    jwks = await response.json()
            public_keys = {}
            
            for key in jwks.get('keys', []):
                kid = key.get('kid')
                if kid:
                    public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(key)
            
            self.logger.info(f"Fetched {len(public_keys)} public keys from Keycloak")
            return public_keys
        
        except Exception as e:
            self.logger.error(f"Failed to fetch public keys: {e}")
            raise AuthException(error_code=AUTH_SERVER_UNAVAILABLE)
    
    async def verify_token(self, token: str, roles: list[str]=None) -> Dict[str, Any]:
        """Verify JWT token, with role verification.
        If any role from the list is present in the user roles he passes."""
        try:
            # Decode header to get public key id to verify the JWT token integrity
            # no need for split when using HTTPBearer
            # token = token.split()[1]
            # self.logger.debug(f"Token: {token}")
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')
            
            if not kid:
                self.logger.debug("No kid")
                raise AuthException(AUTH_INVALID_SESSION)
            
            # Get public keys
            public_keys = await self.__get_public_keys()
            
            if kid not in public_keys:
                # Clear cache and try again, maybe the keys have rotated, or updated
                self.__get_public_keys.cache_clear()
                public_keys = self.__get_public_keys()
                
                if kid not in public_keys:
                    raise AuthException(AUTH_INVALID_SESSION)
            # Verify token
            
            payload = jwt.decode(
                token,
                public_keys[kid],
                algorithms=["RS256"],
                audience=[self.config.client_id,], # add front-end client when it's ready, or else no one will sign in
            )
            # RBAC
            if roles:
                user_roles = payload.get("resource_access", {}).get("eldawood_ecomm", {}).get("roles", [])
                if not any(role in roles for role in user_roles):
                    raise AuthException(AUTH_FORBIDDEN)
            self.logger.info(f"{roles} User {payload.get("name", "..___..")} token verified")
            return payload
            
        
        except jwt.ExpiredSignatureError as e:
            self.logger.debug(str(e))
            raise AuthException(AUTH_TOKEN_EXPIRED)
        except jwt.InvalidTokenError as e:
            if "Audience doesn't match" in str(e):
                raise AuthException(AUTH_INVALID_AUDIENCE)
            raise AuthException(AUTH_INVALID_SESSION)
        except IndexError as e:
            self.logger.debug(str(e))
            raise AuthException(AUTH_INVALID_SESSION)
        except AuthException:
            raise
        except Exception as e:
            error_id = str(uuid.uuid1())
            self.logger.exception("[{error_id}] Unexpected error" + str(e))
            raise AuthException(error_code=UNEXPECTED_ERROR, error_id=error_id)
            
            
if __name__ == "__main__":
    from KeycloakConfig import KeycloakConfig
    from pprint import pprint
    config = KeycloakConfig()
    auth = KeycloakJWTHandler(config)
    
    pprint(auth.verify_token("Bearer token"))