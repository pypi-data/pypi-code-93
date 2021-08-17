from perm_banana import Permission


class MismatchPermissionException(Exception):
    """
    An error that is raised when a set of permissions mismatch by type.
    """

    def __init__(self, permission: Permission, other: Permission):
        self.permission = permission
        self.other = other
        super().__init__(f"The permission {self.permission} is not of the same type as {self.other}")
