from dataclasses import dataclass
from typing import Mapping, Optional, Sequence

from .._utils import Config


@dataclass(frozen=True)
class OidcConfig(Config):
    """The OpenID Connect configuration.

    Atoti+ is compliant with any OpenID Connect OAuth2 authentication provider (Auth0, Google, Keycloak, etc.).

    Example:

        >>> config = {
        ...     "authentication": {
        ...         "oidc": {
        ...             "provider_id": "auth0",
        ...             "issuer_url": "https://example.auth0.com",
        ...             "client_id": "some client ID",
        ...             "client_secret": "some client secret",
        ...             "name_claim": "email",
        ...             "scopes": ["email", "profile"],
        ...             "paths_to_authorities": ["paths/to/authorities"],
        ...             "role_mapping": {
        ...                 "dev_team": {"ROLE_USER", "ROLE_DEV"},
        ...                 "admin": {"ROLE_ADMIN"},
        ...             },
        ...         }
        ...     }
        ... }

        .. doctest::
            :hide:

            >>> validate_config(config)

    """

    provider_id: str
    """The name of the provider.

    It is used to build the redirect URL: ``f"{session_url}/login/oauth2/code/{provider_id}"``.
    """

    issuer_url: str
    """The issuer URL parameter from the provider's OpenID Connect configuration endpoint."""

    client_id: str
    """The app's client ID, obtained from the authentication provider."""

    client_secret: str
    """The app's client secret, obtained from the authentication provider."""

    name_claim: Optional[str] = None
    """The name of the claim in the ID token to use as the name of the user."""

    paths_to_authorities: Optional[Sequence[str]] = None
    """The path to the authorities to use in atoti in the returned access token or ID token."""

    scopes: Optional[Sequence[str]] = None
    """The scopes to request from the authentication provider."""

    role_mapping: Optional[Mapping[str, Sequence[str]]] = None
    """The mapping between the roles returned by the authentication provider and the roles to grant in atoti.

    Users without the role :guilabel:`ROLE_USER` will not have access to the application.
    """
