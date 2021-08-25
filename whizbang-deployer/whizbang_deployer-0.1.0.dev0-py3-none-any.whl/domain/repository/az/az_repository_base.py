import abc
from abc import ABC, abstractmethod

from whizbang.data.az_cli_context import AzCliContext


class IAzRepository(ABC):
    @abstractmethod
    def _execute(self, command: str):
        """the execute interface"""


class AzRepositoryBase(IAzRepository):
    def __init__(self, az_cli_context: AzCliContext):
        self.__context = az_cli_context

    @property
    @abstractmethod
    def _resource_provider(self) -> str:
        """name of the resource provider api"""

    def _execute(self, command: str):
        return self.__context.execute(f'{self._resource_provider} {command} --verbose')
