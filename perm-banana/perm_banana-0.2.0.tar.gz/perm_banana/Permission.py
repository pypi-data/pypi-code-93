from copy import deepcopy


class Permission:
    """A series of permissions, represented as an int"""

    def __init__(self, permissions: int):
        self.permissions = permissions

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({bin(self.permissions)})"

    def __copy__(self) -> "Permission":
        return Permission(self.permissions)

    def __deepcopy__(self, memo) -> "Permission":
        return Permission(deepcopy(self.permissions, memo))

    def __int__(self) -> int:
        return self.permissions

    def __bool__(self) -> bool:
        return bool(self.permissions)

    def __invert__(self):
        return Permission(~self.permissions)

    def __contains__(self, item):
        return not bool(item - self)

    def __and__(self, other):
        return Permission(self.permissions & other.permissions)

    def __iand__(self, other):
        self.permissions &= other.permissions
        return self

    def __or__(self, other):
        return Permission(self.permissions | other.permissions)

    def __ior__(self, other):
        self.permissions |= other.permissions
        return self

    def __add__(self, other):
        return Permission(self.permissions | other.permissions)

    def __iadd__(self, other):
        self.permissions |= other.permissions
        return self

    def __sub__(self, other):
        return Permission(self.permissions & ~other.permissions)

    def __isub__(self, other):
        self.permissions &= ~other.permissions
        return self

    def __lt__(self, other):
        return self.permissions < other.permissions

    def __le__(self, other):
        return self.permissions <= other.permissions

    def __eq__(self, other):
        return self.permissions == other.permissions

    def __ne__(self, other):
        return self.permissions != other.permissions

    def __gt__(self, other):
        return self.permissions > other.permissions

    def __ge__(self, other):
        return self.permissions >= other.permissions
