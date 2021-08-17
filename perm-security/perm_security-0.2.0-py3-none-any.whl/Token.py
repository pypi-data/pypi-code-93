from dataclasses import dataclass
from typing import Set, Optional

from discord import Member
from perm_banana import Permission

from .MemberAdapter.MemberAdapter import MemberAdapter


@dataclass
class Token:
    """An item that allows for a user to achieve a permission otherwise unauthenticated"""

    author: MemberAdapter
    permissions: Permission
    uses: int = 1
    members: Optional[Set[Member]] = None

    def __contains__(self, item: Member):
        """Returns if a member can use a token"""
        if self.members is None:
            return False
        return item in self.members
