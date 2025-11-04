'''
Handles configuration for Keycloak integration
'''
import os
# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

class KeycloakConfig:
    """Contains important keycloak endpoints ready for use"""
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(KeycloakConfig, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.keycloak_url = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
        self.realm = os.getenv("KEYCLOAK_REALM", "my-realm")
        self.client_id = os.getenv("KEYCLOAK_CLIENT_ID", "your-client-id")
        self.client_secret = os.getenv("KEYCLOAK_CLIENT_SECRET", "your-client-secret")
        
    @property
    def jwks_url(self) -> str:
        """To get the JWKS URL for public key verification."""
        return f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/certs"
    
    @property
    def realm_roles_url(self):
        """GET for all realm roles, POST to create a realm role.
        More at https://www.keycloak.org/docs-api/latest/rest-api/index.html#_roles
        """
        return f"{self.keycloak_url}/admin/realms/{self.realm}/roles"

    @property
    def token_url(self) -> str:
        """OpenID Connect token endpoint for authentication workflow.
        POST to retrieve access token, refresh token, etc.
        More at https://www.keycloak.org/docs/latest/authorization_services/index.html#_service_obtaining_permissions
        """
        return f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/token"
    
    def available_client_user_role_url(self, user_id: str, client_id) -> str:
        """Use GET to get available client-level roles that can be mapped to user <br>
        more at https://www.keycloak.org/docs-api/latest/rest-api/index.html#_users"""
        return f"{self.keycloak_url}/admin/realms/{self.realm}/users/{user_id}/role-mappings/clients/{client_id}/available"
    
    def client_role_mapping_url(self, user_id: str, client_id) -> str:
        """Use POST to attach role to user, 
        <br>DELETE to remove role from user, <br>
        more at https://www.keycloak.org/docs-api/latest/rest-api/index.html#_users"""
        return f"{self.keycloak_url}/admin/realms/{self.realm}/users/{user_id}/role-mappings/clients/{client_id}"
    
    def user_url(self, user_id: str) -> str:
        """Use PUT to update the user GET to get user representation, DELETE to delete user, <br>
        more at https://www.keycloak.org/docs-api/latest/rest-api/index.html#_users <br>
        it returns https://www.keycloak.org/docs-api/latest/rest-api/index.html#UserRepresentation"""
        return f"{self.keycloak_url}/admin/realms/{self.realm}/users/{user_id}"    

    
    def realm_role_url(self, role_name):
        """GET to fetch realm role details, PUT to update, DELETE to remove.
        More at https://www.keycloak.org/docs-api/latest/rest-api/index.html#_roles
        """
        return f"{self.keycloak_url}/admin/realms/{self.realm}/roles/{role_name}"

    def realm_role_mapping_url(self, user_id):
        """GET/POST to fetch or assign realm-level roles for user,<br>
        DELETE to remove realm-level roles from user.
        More at https://www.keycloak.org/docs-api/latest/rest-api/index.html#_users
        """
        return f"{self.keycloak_url}/admin/realms/{self.realm}/users/{user_id}/role-mappings/realm"

    def client_roles_url(self, client_id):
        """GET all client-level roles, POST to create one for a client.
        More at https://www.keycloak.org/docs-api/latest/rest-api/index.html#_roles
        """
        return f"{self.keycloak_url}/admin/realms/{self.realm}/clients/{client_id}/roles"

    def client_role_detail_url(self, client_id, role_name):
        """GET, PUT, DELETE a specific client-level role.
        More at https://www.keycloak.org/docs-api/latest/rest-api/index.html#_roles
        """
        return f"{self.keycloak_url}/admin/realms/{self.realm}/clients/{client_id}/roles/{role_name}"

    # # To get the user information.
    # # takes JWT token of the user with bearer word in header and returns his data
    # @property
    # def userinfo_url(self) -> str:
    #     return f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/userinfo"