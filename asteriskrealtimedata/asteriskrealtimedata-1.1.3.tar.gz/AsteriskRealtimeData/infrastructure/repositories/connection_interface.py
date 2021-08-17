from abc import ABC, abstractmethod
from typing import Any
from antidote import inject
from AsteriskRealtimeData.environments import Config


class Connection(ABC):
    _host: str
    _port: int
    _user: str
    _password: str
    _database: str

    @inject([Config.HOST, Config.PORT, Config.USER, Config.PASSWORD, Config.DATABASE])
    def __init__(self, host: str, port: int, user: str, password: str, database: str) -> None:
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database

    @abstractmethod
    def connect(self, server: str, port: int, user: str, password: str, database: str) -> None:
        raise NotImplementedError("Method connect must be implemented")

    @abstractmethod
    def get_connection(self) -> Any:
        raise NotImplementedError("Method get_connection must be implemented")

    def getHost(self) -> str:
        return self._host

    def getPort(self) -> int:
        return self._port

    def getUser(self) -> str:
        return self._user

    def getPassword(self) -> str:
        return self._password

    def getDatabase(self) -> str:
        return self._database
