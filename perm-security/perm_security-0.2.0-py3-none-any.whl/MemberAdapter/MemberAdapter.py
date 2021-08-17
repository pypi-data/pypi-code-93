from abc import ABC, abstractmethod

from discord import Member
from perm_banana import Permission


class MemberAdapter(ABC):
    """
    A Discord Member with extended attributes to enable better Permission handling.
    """

    member: Member

    def __init__(self, member: Member, *args, **kwargs):
        self.member = member

    def __validate__(self, other) -> bool:
        return True

    @property
    @abstractmethod
    def permissions(self) -> Permission:
        """
        The permission of the member in a given context.

        Returns
        -------
        Permission
            The permissions a user has in a given context determined by the MemberAdapter class.
        """
