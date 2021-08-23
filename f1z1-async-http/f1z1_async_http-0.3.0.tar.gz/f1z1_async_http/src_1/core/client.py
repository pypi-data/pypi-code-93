# @Time     : 2021/5/30
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from operator import not_
from typing import AnyStr, Optional

from httpx import Response

from ..components.conf import IConfig, Config
from ..components.event_hook import AbstractEventHooksManager
from ..components.notifies import IAsyncNotifierManager, NotifierManagerFactory
from ..components.options import IRequestOptions
from .aclient import AsyncClientBuilder
from .switch import Switch


class IAsyncHttpClient(object):

    async def request(self, method: str, url: AnyStr, options: Optional[IRequestOptions]) -> Response:
        raise NotImplementedError("")

    async def __aenter__(self) -> ["IAsyncHttpClient"]:
        raise NotImplementedError("")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError("")


class AsyncHttpClient(IAsyncHttpClient):

    def __init__(self,
                 config: Optional[IConfig] = None,
                 hooks: Optional[AbstractEventHooksManager] = None):
        self._config = config if config else Config()
        self._notifier = NotifierManagerFactory.create(hooks)
        self._switch = Switch(self._notifier)
        self._client = self._init_httpx(self._config, self._notifier)

    @property
    def client(self):
        return self._client

    def _get_options(self, options: Optional[IRequestOptions]):
        return {} if not_(options) else options.as_dict()

    async def request(self, method: str, url: AnyStr, options: Optional[IRequestOptions]):
        return await self._send(method, url, options)

    async def _send(self, method: str, url: AnyStr, options: Optional[IRequestOptions]):
        return await self.client.request(
            method, url, **self._get_options(options)
        )

    async def __aenter__(self):
        await self._switch.open(self.client)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._switch.close(self.client)

    def _init_httpx(self, config: IConfig, notifier: IAsyncNotifierManager):
        builder = AsyncClientBuilder()
        builder \
            .set_base_url(config.base_url) \
            .set_max_connection(config.max_connection) \
            .set_max_keepalive(config.max_keepalive) \
            .set_timeout(config.timeout) \
            .set_event_hooks(notifier.as_dict())

        return builder.build()

    def __str__(self):
        return f"{self.__class__.__name__}(notifier={str(self._notifier)}, completed={self._notifier.completed})"
