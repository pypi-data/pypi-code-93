from dataclasses import dataclass
from typing import Mapping, Optional, Sequence

from .._utils import Config


@dataclass(frozen=True)
class LdapConfig(Config):
    """
    The LDAP configuration.

    Example:

        >>> config = {
        ...     "authentication": {
        ...         "ldap": {
        ...             "url": "ldap://example.com:389",
        ...             "base_dn": "dc=example,dc=com",
        ...             "user_search_base": "ou=people",
        ...             "group_search_base": "ou=roles",
        ...             "role_mapping": {
        ...                 "admin": {"ROLE_ADMIN"},
        ...                 "france": {"ROLE_FRANCE", "ROLE_EUR"},
        ...             },
        ...         }
        ...     }
        ... }

        .. doctest::
            :hide:

            >>> validate_config(config)

    """

    url: str
    """The LDAP URL including the protocol and port."""

    base_dn: str
    """The Base Distinguished Name of the directory service."""

    user_search_filter: str = "(uid={0})"
    """The LDAP filter used to search for users.

    The substituted parameter is the user's login name.
    """

    user_search_base: str = ""
    """Search base for user searches."""

    group_search_filter: str = "(uniqueMember={0})"
    """The LDAP filter to search for groups.

    The substituted parameter is the DN of the user.
    """

    group_search_base: str = ""
    """The search base for group membership searches."""

    group_role_attribute_name: str = "cn"
    """The attribute name that maps a group to a role."""

    role_mapping: Optional[Mapping[str, Sequence[str]]] = None
    """The mapping between the roles returned by the LDAP authentication provider and the corresponding roles to use in atoti.

    LDAP roles are case insensitive.

    Users without the role :guilabel:`ROLE_USER` will not have access to the application.
    """
