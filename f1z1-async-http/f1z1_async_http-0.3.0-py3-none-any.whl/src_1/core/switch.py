# @Time     : 2021/7/18
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from abc import ABCMeta, abstractmethod
from operator import not_

from httpx import AsyncClient

from ..components.notifies import IAsyncNotifierManager


class ISwitch(metaclass=ABCMeta):

    @abstractmethod
    async def open(self, client: AsyncClient) -> None:
        pass

    @abstractmethod
    async def close(self, client: AsyncClient) -> None:
        pass


class Switch(ISwitch):

    def __init__(self, notifier: IAsyncNotifierManager):
        self._notifier = notifier

    async def open(self, client: AsyncClient) -> None:
        if self.is_closed(client):
            await client.__aenter__()

    async def close(self, client: AsyncClient) -> None:
        if all([not self.is_closed(client), self.is_completed()]):
            await client.aclose()

    def is_closed(self, client: AsyncClient):
        return client.is_closed

    def is_completed(self):
        return True if not_(self._notifier) else self._notifier.completed
