"""
Need extra django settings configuration

SSO={
    "SERVER_URL": <sso url>,
    "REALM": <sso api realm>,
    "CLIENT_ID": <sso client id api>,
    "CLIENT_SECRET_KEY": <sso client secret see Client credentials>,
    "ADMIN_LOGIN": <optional: sso admin user>
    "ADMIN_PASSWORD": <optional: sso admin password>
}
"""
from typing import Optional

from django.conf import settings
from keycloak import KeycloakOpenID, KeycloakAdmin
from rest_framework.exceptions import AuthenticationFailed

from w.services.abstract_service import AbstractService
from django.utils.translation import gettext as _

from w.services.technical.models.sso import SsoValidToken


class SsoService(AbstractService):
    _keycloak_session: KeycloakOpenID = None
    _keycloak_admin: KeycloakAdmin = None
    _clients: Optional[dict] = None
    _client_roles: dict = {}

    @classmethod
    def clear(cls):
        cls._keycloak_session = None
        cls._keycloak_admin = None
        cls._clients = None
        cls._client_roles = {}

    @classmethod
    def _is_initialized(cls):
        return cls._keycloak_session is not None

    @classmethod
    def _init_keycloak_admin(cls):
        if "ADMIN_LOGIN" in settings.SSO and "ADMIN_PASSWORD" in settings.SSO:
            cls._keycloak_admin = cls._get_keycloak_admin()
            return cls._keycloak_admin

        raise RuntimeError("Missing SSO settings ADMIN_LOGIN or ADMIN_PASSWORD")

    @classmethod
    def _check_admin_is_initialized(cls):
        cls._check_is_initialized()

        if cls._keycloak_admin is not None:
            return cls._keycloak_admin

        return cls._init_keycloak_admin()

    @classmethod
    def _get_keycloak_admin(cls):  # pragma: no cover
        """Only to simplify tests"""
        kc = KeycloakAdmin(
            server_url=settings.SSO["SERVER_URL"],
            username=settings.SSO["ADMIN_LOGIN"],
            password=settings.SSO["ADMIN_PASSWORD"],
            realm_name="master",
        )
        kc.realm_name = settings.SSO["REALM"]
        return kc

    @classmethod
    def init(cls) -> None:
        """Initialize service
        config(dict): Sso configuration:
            server_url(str): sso server url
            realm_name(str): realm name
            client_id(str): client id
            client_secret_key(str): client secret
        """
        config = {
            "server_url": settings.SSO["SERVER_URL"],
            "realm_name": settings.SSO["REALM"],
            "client_id": settings.SSO["CLIENT_ID"],
            "client_secret_key": settings.SSO["CLIENT_SECRET_KEY"],
        }
        cls._keycloak_session = KeycloakOpenID(**config)

    @classmethod
    def _sso_introspect(cls, token):  # pragma: no cover
        return cls._keycloak_session.introspect(token)

    @classmethod
    def get_clients(cls):
        # need client role: realm-management:manage-users
        if cls._clients is None:
            cls._check_admin_is_initialized()
            clients = cls._keycloak_admin.get_clients()
            cls._clients = {c["clientId"]: c["id"] for c in clients}
        return cls._clients

    @classmethod
    def is_token_valid(cls, token):
        cls._check_is_initialized()
        decoded_token = cls._sso_introspect(token)
        if decoded_token.get("active", False):
            return SsoValidToken(decoded_token)
        raise AuthenticationFailed(_("Invalid or expired token."))

    @classmethod
    def create_user(cls, user: dict):
        # need client role: realm-management:manage-users
        return cls._keycloak_admin.create_user(
            {
                "email": user["email"],
                "username": user["username"],
                "enabled": True,
                "firstName": user["first_name"],
                "lastName": user["last_name"],
                "credentials": [{"value": user["password"], "type": "password"}],
            }
        )

    @classmethod
    def add_client_role(cls, user_id, client_id, roles):
        res = cls._keycloak_admin.assign_client_role(user_id, client_id, roles)
        return res

    @classmethod
    def get_client_roles(cls, client_id):
        if client_id not in cls._client_roles:
            cls._check_admin_is_initialized()
            cls._client_roles[client_id] = {
                r["name"]: r for r in cls._keycloak_admin.get_client_roles(client_id)
            }
        return cls._client_roles[client_id]

    @classmethod
    def _add_client_roles(cls, user_id, client_roles):
        clients = cls.get_clients()
        for client, roles in client_roles.items():
            client_id = clients[client]
            client_roles = cls.get_client_roles(client_id)
            roles = [client_roles[r] for r in roles]
            cls.add_client_role(user_id, client_id, roles)

    @classmethod
    def get_or_create_user(cls, user: dict):
        """
        Args:
                "email": "example@example.com",
                "username": "example@example.com",
                "first_name": "Example",
                "last_name": "Example",
                "password": "astrongpassword",
                "client_roles": {
                    "<clientId>": ["role1", ...],
                    "<clientId>": ["roles"]
                    ...
                }
            }

        Need Keycloak real-management roles:
            - manage-users
            - views-client
        """
        cls._check_admin_is_initialized()
        user_id = cls._keycloak_admin.get_user_id(user["username"])
        if not user_id:
            user_id = cls.create_user(user)
            cls._add_client_roles(user_id, user["client_roles"])

        user = cls._keycloak_admin.get_user(user_id)
        return user

    @classmethod
    def require_update_password(
        cls, user_id: str, client_id=str, lifespan=None, redirect_uri=None
    ):
        cls._check_admin_is_initialized()
        return cls._keycloak_admin.send_update_account(
            user_id=user_id,
            payload=["UPDATE_PASSWORD"],
            client_id=client_id,
            lifespan=lifespan,
            redirect_uri=redirect_uri,
        )
