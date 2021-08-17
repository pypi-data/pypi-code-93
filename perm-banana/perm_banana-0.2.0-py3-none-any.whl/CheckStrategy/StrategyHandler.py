from .StrategyCheck import StrategyCheck

from ..PermissionHandler import PermissionHandler


class StrategyHandler(StrategyCheck):
    """
    A Strategy for determining if a handler is a subset of another handler.
    """

    def _strategy(self, permission: PermissionHandler) -> bool:
        """
        Checks against the permission of a class.
        If the handler provided are inside the monitored handler, then
        the method will yield True.
        """
        return not bool(self.check.permission - permission)
