"""Access enums for repositories"""
from taktile_types.enums.common import ExtendedEnum


class AccessKind(ExtendedEnum):
    """Kinds of access to a repository"""

    OWNER = "owner"
    VIEWER = "viewer"
