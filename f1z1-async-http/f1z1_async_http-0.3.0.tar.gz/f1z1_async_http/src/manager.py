# @Time     : 2021/8/23
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from abc import abstractmethod
from typing import Optional
from .client import Client


class Manager:

    @abstractmethod
    def get(self, name: str) -> Optional[Client]:
        pass

    @abstractmethod
    def set(self, name: str, client: Client):
        pass

    @abstractmethod
    def remove(self, name: str):
        pass

    @abstractmethod
    def clear(self):
        pass


class ClientManager(Manager):
    __shared = {}

    def __init__(self):
        self.__dict__ = ClientManager.__shared

    def get(self, name: str) -> Optional[Client]:
        return getattr(self, name, None)

    def set(self, name: str, client: Client):
        setattr(self, name, client)

    def remove(self, name: str) -> Client:
        delattr(self, name)

    def clear(self) -> None:
        ClientManager.__shared.clear()
        self.__dict__ = ClientManager.__shared
