from perm_banana import Permission

from ..MemberAdapter.MemberAdapter import MemberAdapter


class PermissionDeniedException(Exception):
    """
    An error that is raised when a member does not have permission to do something.
    """

    def __init__(self, permissions: Permission, member: MemberAdapter):
        self.permissions = permissions
        self.member = member
        super().__init__(f"Member {self.member} does not have the permissions {permissions - self.member.permissions}")
