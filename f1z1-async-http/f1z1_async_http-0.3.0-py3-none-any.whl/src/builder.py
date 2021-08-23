# @Time     : 2021/8/22
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from abc import abstractmethod
from operator import not_
from typing import Dict, Optional, Union

from httpx import AsyncClient, Response, Limits, Timeout
from f1z1_common.src.is_ import is_validate

from ..components.hook import Hook
from ..components.options import Options
from .client import Client, HttpClient
from .defaults import DEFAULT_LIMITS, DEFAULT_TIMEOUT
from .manager import ClientManager

OptionsType = Dict
GET = "GET"
POST = "POST"
_M2S = {GET: "GET", POST: "POST"}
_S2M = {"GET": GET, "POST": POST}


def s2m(method: str):
    return _M2S[_S2M.get(method.upper(), GET)]


class RequestBuilder:
    _manager = ClientManager()

    def __init__(self):
        self._hook: Hook = None
        self._options = Options()

    def add_cookies(self, cookies: OptionsType):
        return self.update("cookies", cookies)

    def add_data(self, data: OptionsType):
        return self.update("data", data)

    def add_headers(self, headers: OptionsType):
        return self.update("headers", headers)

    def add_json(self, json: OptionsType):
        return self.update("json", json)

    def add_params(self, params: OptionsType):
        return self.update("params", params)

    def set_hook(self, hook: Hook):
        if isinstance(hook, Hook):
            self._hook = hook
        return self

    @abstractmethod
    async def request(self, method: str, url: str) -> Response:
        pass

    @abstractmethod
    async def post(self, url: str) -> Response:
        pass

    @abstractmethod
    async def get(self, url: str) -> Response:
        pass

    def update(self, key: str, options: Dict):
        self._options.update(key, options)
        return self

    def _to_kwargs(self):
        options = self._options.as_dict()
        if not_(options):
            return {}
        self._options.clear()
        return options

    @classmethod
    def get_instance(cls, name: str) -> Optional[Client]:
        return cls._manager.get(name)

    @classmethod
    def set_instance(cls, name: str, client: Client):
        cls._manager.set(name, client)

    @classmethod
    def clear_instance(cls):
        cls._manager.clear()


class AsyncRequestBuilder(RequestBuilder):
    _base_url = ""
    _limits = DEFAULT_LIMITS
    _timeout = DEFAULT_TIMEOUT

    def __init__(self, name: str = "default"):
        super().__init__()
        self._name = name
        self._options = Options()

    def set_base_url(self, base_url: str):
        if is_validate.is_string(base_url):
            self._base_url = base_url
        return self

    def set_limits(self, max_connections: int, max_keepalive: int):
        self._limits = Limits(max_connections=max_connections, max_keepalive_connections=max_keepalive)
        return self

    def set_timeout(self, timeout: Union[int, float]):
        self._timeout = Timeout(timeout)
        return self

    async def post(self, url: str):
        return await self.request(POST, url)

    async def get(self, url: str):
        return await self.request(GET, url)

    async def request(self, method: str, url: str):
        instance = self.build()
        async with instance as http:
            return await http.request(s2m(method), url, **self._to_kwargs())

    def build(self):
        key = self._name
        instance = self.get_instance(key)
        if not_(instance):
            instance = HttpClient(self._create_async_client(), self._hook)
            self.set_instance(key, instance)
        return instance

    def __str__(self):
        return f"{self.__class__.__name__}(name={self._name}, hook={self._hook})"

    def _create_async_client(self):
        return AsyncClient(
            base_url=self._base_url,
            limits=self._limits,
            timeout=self._timeout
        )
