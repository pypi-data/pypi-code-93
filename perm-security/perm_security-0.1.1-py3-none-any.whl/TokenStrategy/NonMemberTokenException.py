from perm_banana import Permission

from ..MemberAdapter.MemberAdapter import MemberAdapter


class NonMemberTokenException(Exception):
    """
    An error that is raised when no members are provided.
    """

    def __init__(self, member: MemberAdapter, permissions: Permission, uses: int, duration: float):
        self.member = member
        self.permissions = permissions
        self.uses = uses
        self.duration = duration
        super().__init__(
            f"{self.member} did not provide any members for their token with "
            f"permissions: {self.permissions}, {self.uses} uses, and a duration of {self.duration}"
        )
