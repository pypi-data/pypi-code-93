from typing import Optional, Union

from .Permission import Permission
from .PermissionHandler import PermissionHandler
from .MetaCheck import MetaCheck
from .NameConflictException import NameConflictException

from .CheckStrategy.Strategy import Strategy


Perm = Union[Permission, PermissionHandler]


class Check(MetaCheck):
    def __init__(
        self, permission: Perm, permission_name: str = "permissions", strategy: Optional[Strategy] = None
    ) -> None:

        self._permission = permission
        self._permission_name = permission_name

        # To prevent a circular import, we import inside the class.
        if not strategy:
            from .CheckStrategy.StrategyPermissions import StrategyPermissions

            strategy = StrategyPermissions(self)
        super().__init__(strategy.strategy)

    def __repr__(self) -> str:
        if self._permission_name == "permissions":
            return f"{self.__class__.__name__}({self._permission})"
        else:
            return f"{self.__class__.__name__}({self._permission}, permission_name={self._permission_name})"

    def __and__(self, other):
        if self._permission_name != other._permission_name:
            raise NameConflictException(self._permission_name, other._permission_name)
        return Check(self._permission & other._permission, self._permission_name)

    def __or__(self, other):
        if self._permission_name != other._permission_name:
            raise NameConflictException(self._permission_name, other._permission_name)
        return Check(self._permission | other._permission, self._permission_name)

    @classmethod
    def from_int(cls, permission: int, permission_name: str = "permissions"):
        return cls(Permission(permission), permission_name)

    @property
    def permission(self) -> Perm:
        return self._permission

    @property
    def permission_name(self) -> str:
        return self._permission_name
