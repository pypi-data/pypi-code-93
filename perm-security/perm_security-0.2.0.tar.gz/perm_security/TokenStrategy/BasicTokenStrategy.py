from typing import Optional, Set
from copy import deepcopy

from discord import Member
from perm_banana import Permission

from ..Token import Token
from ..MemberAdapter.MemberAdapter import MemberAdapter

from .TokenHandlerStrategy.TokenHandlerStrategy import TokenHandlerStrategy

from .MismatchPermissionException import MismatchPermissionException
from .PermissionDeniedException import PermissionDeniedException

from .NonMemberTokenException import NonMemberTokenException
from .TokenStrategy import TokenStrategy


class BasicTokenStrategy(TokenStrategy):
    """A series of commands to be used to generate tokens"""

    def __init__(self, handler: TokenHandlerStrategy):
        self.handler = handler
        super().__init__()

    async def generate_token(
        self,
        author: MemberAdapter,
        permissions: Permission,
        members: Optional[Set[Member]],
        uses: int = 1,
        duration: float = 60.0,
    ):
        if type(author.permissions) != type(permissions):
            raise MismatchPermissionException(author.permissions, permissions)
        if permissions - author.permissions:
            raise PermissionDeniedException(permissions, author)
        if members is None:
            raise NonMemberTokenException(author, permissions, uses, duration)
        self.handler.add_token(Token(author, permissions, uses, members), duration)

    async def find_permissions_from_tokens(self, member: MemberAdapter, permissions: Permission) -> bool:
        """
        Determines if a Member has permissions from any active Tokens.
        If the Member does, the function will try to wisely use the Tokens and return True.

        Parameters
        ----------
        member : MemberAdapter
            The Member that is attempting the action.
        permissions : Permission
            The remaining permissions required to be fulfilled by Tokens.

                It is assumed that all Permissions that remain are solely to be achieved through Tokens.
                The Permissions of the User should be deducted prior to calling the method.

        Returns
        -------
        bool
            If the Member has the required Permissions.
        """
        # Do no touch the provided permissions as they will be used to determine Token later.
        remaining_permission = deepcopy(permissions)
        tokens = self.handler.get_tokens(member)
        for token_id in tokens:
            remaining_permission -= self.handler.get_token(token_id).permissions
            if not remaining_permission:
                break  # The Member has the Tokens to do it!
        else:
            return False

        for token in tokens:
            self.handler.use_token(token)

        return True

    async def has_permissions(self, member: MemberAdapter, permissions: Permission) -> bool:
        if type(member.permissions) != type(permissions):
            raise MismatchPermissionException(member.permissions, permissions)

        permission_required = permissions - member.permissions

        if not permission_required:
            # The Member already has the permissions required.
            return True

        return await self.find_permissions_from_tokens(member, permissions)
