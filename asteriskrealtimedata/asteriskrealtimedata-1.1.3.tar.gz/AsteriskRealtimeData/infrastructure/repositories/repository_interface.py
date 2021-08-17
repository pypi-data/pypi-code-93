from abc import ABC, abstractmethod
from antidote import inject, Provide
from AsteriskRealtimeData.infrastructure.repositories.connection_interface import (
    Connection,
)


class Repository(ABC):
    __tablename__: str

    @abstractmethod
    def __init__(self, connection: Provide[Connection]) -> None:
        self.connection = connection
        super().__init__()

    @abstractmethod
    def save(self):
        raise NotImplementedError

    @abstractmethod
    def list(self):
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self):
        raise NotImplementedError

    @abstractmethod
    def delete_by_id(self):
        raise NotImplementedError

    @abstractmethod
    def get_by_criteria(self):
        raise NotImplementedError

    @abstractmethod
    def delete_by_criteria(self):
        raise NotImplementedError

    def get_table_name(self):
        return self.__tablename__
