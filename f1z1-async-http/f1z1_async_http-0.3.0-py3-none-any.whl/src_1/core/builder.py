# @Time     : 2021/7/17
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from abc import ABCMeta, abstractmethod
from typing import AnyStr

from httpx import Response

from ..components.conf import IConfig, ConfigManager
from ..components.event_hook import AbstractEventHooksManager, FunctionHooksManager, HookOrAFunc
from ..components.options import RequestOptions
from .factory import AsyncHttpClientFactory


class AbstractRequestBuilder(metaclass=ABCMeta):

    def __init__(self):
        self._configs = ConfigManager()
        self._options = RequestOptions()
        self._hooks = FunctionHooksManager()

    def add_cookies(self, key, value):
        self._options.add_cookies(key, value)
        return self

    def add_data(self, key, value):
        self._options.add_data(key, value)
        return self

    def add_headers(self, key, value):
        self._options.add_headers(key, value)
        return self

    def add_json(self, key, value):
        self._options.add_json(key, value)
        return self

    def add_params(self, key, value):
        self._options.add_params(key, value)
        return self

    def add_event_hook(self, key: str, hook_or_afunc: HookOrAFunc):
        self._hooks.set(key, hook_or_afunc)
        return self

    def set_hooks(self, hooks: AbstractEventHooksManager):
        self._check_hooks(hooks)
        self._hooks = hooks
        return self

    def _check_config(self, value):
        if not isinstance(value, IConfig):
            raise ValueError(f"config need IConfig, but got {type(value).__name__}")

    def _check_hooks(self, value):
        if not isinstance(value, AbstractEventHooksManager):
            raise ValueError(f"interceptors need AbstractEventHooksManager, but got {type(value).__name__}")

    @abstractmethod
    async def request(self, method: str, url: AnyStr) -> Response:
        pass

    @abstractmethod
    async def post(self, url: AnyStr) -> Response:
        pass

    @abstractmethod
    async def get(self, url: AnyStr) -> Response:
        pass

    def __str__(self):
        return f"{self.__class__.__name__}(options={self._options}, hooks={self._hooks})"


class AsyncRequestBuilder(AbstractRequestBuilder):

    def __init__(self):
        super().__init__()
        self._config_node = "default"

    def set_config(self, node: str, config: IConfig):
        self._check_config(config)
        self._config_node = node
        self._configs.set(node, config)
        return self

    async def request(self, method: str, url: AnyStr) -> Response:
        http = self._get_instance()
        async with http:
            return await http.request(method, url, self._options)

    async def post(self, url: AnyStr) -> Response:
        return await self.request("POST", url)

    async def get(self, url: AnyStr) -> Response:
        return await self.request("GET", url)

    def _get_instance(self):
        node = self._config_node
        config = self._configs.get(node)
        factory = AsyncHttpClientFactory(node, config, self._hooks)
        return factory.create()
