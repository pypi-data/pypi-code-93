from .StrategyCheck import StrategyCheck

from ..Permission import Permission


class StrategyPermission(StrategyCheck):
    """
    A Strategy for determining if a permission is a subset of another permission.
    """

    def _strategy(self, permission: Permission) -> bool:
        """
        Checks against the permission of a class.
        If the permissions provided are inside the monitored permission, then
        the method will yield True.
        """
        return self.check.permission in permission
