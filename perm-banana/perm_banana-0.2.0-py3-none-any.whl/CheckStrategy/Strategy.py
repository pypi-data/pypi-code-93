from typing import Any
from abc import ABC, abstractmethod


class Strategy(ABC):
    """
    A strategy for determining if a Check will return True or False.
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    @abstractmethod
    def strategy(self, object: Any) -> bool:
        """
        The strategy for determining if a given object matches with the Check.
        """
