from abc import ABC, abstractmethod


class ConnectionData(ABC):
    @abstractmethod
    def url(self) -> str:
        pass

    @abstractmethod
    def username(self) -> str:
        pass

    @abstractmethod
    def password(self) -> str:
        pass
