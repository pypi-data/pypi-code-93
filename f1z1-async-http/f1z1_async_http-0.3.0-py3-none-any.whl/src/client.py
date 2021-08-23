# @Time     : 2021/8/23
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from abc import abstractmethod
from operator import not_
from typing import NoReturn

from httpx import AsyncClient, Response, TimeoutException

from ..components.hook import Hook
from ..components.notifier import NumCounter, Notifier, REQNotifier, RESPNotifier


class ISwitch:

    @abstractmethod
    async def open(self, client: AsyncClient) -> NoReturn:
        pass

    @abstractmethod
    async def close(self, client: AsyncClient) -> NoReturn:
        pass


class Switch(ISwitch):

    def __init__(self):
        self._is_closed = True

    async def open(self, client: AsyncClient) -> NoReturn:
        self._set_closed(client)
        if self.is_closed():
            await client.__aenter__()

    async def close(self, client: AsyncClient) -> NoReturn:
        self._set_closed(client)
        if not_(self.is_closed()):
            await client.aclose()

    def is_closed(self):
        return self._is_closed

    def _set_closed(self, client: AsyncClient):
        self._is_closed = client.is_closed

    def __str__(self):
        return f"{self.__class__.__name__}(is_closed={self.is_closed()})"


class Client:

    @abstractmethod
    async def request(self, method: str, url: str, **kwargs) -> Response:
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> NoReturn:
        pass

    @abstractmethod
    async def __aenter__(self) -> "Client":
        pass


class HttpClient(Client):

    def __init__(self, client: AsyncClient, hook: Hook = None):
        self._client = client
        self._hook = hook

        self._counter = NumCounter()
        self._switch = Switch()
        self.update_hook(self._hook)

    @property
    def client(self):
        return self._client

    async def request(self, method: str, url: str, **kwargs) -> Response:
        try:
            return await self.client.request(method, url, **kwargs)
        except TimeoutException:
            self.clear()
            await self.safe_close()

    async def __aenter__(self) -> Client:
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.safe_close()

    async def open(self):
        await self._switch.open(self.client)

    async def safe_close(self):
        print(f"{self.is_completed()}")
        if self.is_completed():
            await self._switch.close(self.client)

    def clear(self):
        self._counter.clear()

    def update_hook(self, hook: Hook = None):
        self.client.event_hooks = {
            "request": self.to_list(REQNotifier(self._counter, hook)),
            "response": self.to_list(RESPNotifier(self._counter, hook))
        }

    def to_list(self, notifier: Notifier):
        return notifier.to_list()

    def is_completed(self):
        return not_(self._counter.count)

    def __str__(self):
        return f"{self.__class__.__name__}(client={self.client}, is_completed={self.is_completed()})"
