from typing import Union

from ..Check import Check
from ..Permission import Permission
from ..PermissionHandler import PermissionHandler

from .StrategyCheck import StrategyCheck
from .StrategyHandler import StrategyHandler
from .StrategyPermission import StrategyPermission


class StrategyPermissions(StrategyCheck):
    """
    A strategy for determining the contents of a Permission or a PermissionHandler.
    """

    def __init__(self, check: Check):
        super().__init__(check=check)
        self._permission_strategy = StrategyPermission(check=check)
        self._handler_strategy = StrategyHandler(check=check)

    def _strategy(self, permission: Union[Permission, PermissionHandler]) -> bool:
        if isinstance(permission, Permission):
            return self._permission_strategy._strategy(permission)
        elif isinstance(permission, PermissionHandler):
            return self._handler_strategy._strategy(permission)
        else:
            raise NotImplementedError(f"{self} does not implement a check for {permission.__class__.__name__}")
