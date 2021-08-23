from dataclasses import dataclass
from typing import Optional

from .._utils import Config


@dataclass(frozen=True)
class BasicAuthenticationConfig(Config):
    """
    The Basic Authentication configuration.

    Basic authentication is the easiest way to set up security since it only requires defining the users, their password, and their roles.
    """

    realm: Optional[str] = None
    """The realm describing the protected area.

    Different realms can be used to isolate sessions running on the same domain (regardless of the port).
    The realm will also be displayed by the browser when prompting for credentials.
    Defaults to ``f"{session_name} atoti session at {session_id}"``.

    Example:

        >>> config = {"authentication": {"basic": {"realm": "Example"}}}

        .. doctest::
            :hide:

            >>> validate_config(config)

    """
