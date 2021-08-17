from typing import Optional, Set
from abc import ABC, abstractmethod

from discord import Member
from perm_banana import Permission

from ..MemberAdapter.MemberAdapter import MemberAdapter


class TokenStrategy(ABC):
    """A series of commands to be used to generate tokens"""

    @abstractmethod
    async def generate_token(
        self,
        author: MemberAdapter,
        permissions: Permission,
        members: Optional[Set[Member]],
        uses: int = 1,
        duration: float = 60.0,
    ):
        """
        Generates a Member defined Token by the Author.

        Parameters
        ----------
        author : MemberAdapter
            The creator of the Token.
        permissions : Permission
            The Permission the Token will grant.

                If the Permissions the Author has do not allign with the Permissions of the Token, then
                a MismatchPermissionException will be raised.

                If the Author does not have Permission to create such a Token,
                then a PermissionDeniedException will be raised.

        members : Optional[Set[Member]]
            The Members that the Token can be used by.
        uses : int, optional
            The amount of times the Token can be used before it is consumed, by default 1
        duration : float, optional
            The amount of seconds before the Token is automatically destroyed, by default 60.0
        """

    @abstractmethod
    async def has_permissions(self, member: MemberAdapter, permissions: Permission) -> bool:
        """
        Checks whether the Member specified has the Permissions specified and utilizes any Tokens required.

        Parameters
        ----------
        member : MemberAdapter
            The Member that will be doing the action.
        permissions : Permission
            The Permissions that are required to do the action.

        Returns
        -------
        bool
            Whether or not the Member can preform the action.

                If the Member can preform the action, then the Tokens that gave any permissions,
                will be used automatically.  If the Member cannot preform the action, the Tokens
                will not be used.
        """
