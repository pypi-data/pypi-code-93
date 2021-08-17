from typing import TypeVar, Any
from abc import ABC, abstractmethod

from .Strategy import Strategy

from ..Check import Check


T = TypeVar("T")


class StrategyCheck(Strategy, ABC):
    """
    An extension of Strategy that adds data for using Check instead of MetaCheck.
    """

    def __init__(self, check: Check):
        self._check = check

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.check})"

    @property
    def check(self) -> Check:
        """Returns the instance of the check to be changed"""

        # The check is a descriptor, so if we used get(), then it would return the result
        # of the descriptor which is undesired.  Instead, we must manually get around
        # the descriptor by finding it in the class dictionary.
        return self.__dict__["_check"]

    def _get_current_permissions(self, object: T) -> T:
        """
        Retrieves the current object and attempts to find the permission defined by
        the attribute _permission_name.  If it fails to find the permission, an error
        will be raised.
        """
        if getattr(object, "__banana", False):
            # The object itself is the Permission or Handler!
            current_permissions = object
        else:
            current_permissions = getattr(object, self.check.permission_name, None)
        if current_permissions is None:
            raise AttributeError(f"{object} has no variable {self.check.permission_name} to check")
        return current_permissions

    def strategy(self, object: Any) -> bool:
        """
        Finds the current permission and pass it to the next method to determine its
        results.
        """
        return self._strategy(self._get_current_permissions(object))

    @abstractmethod
    def _strategy(self, permission: Any) -> bool:
        """
        The strategy for determining if a given object matches with the Check.
        """
