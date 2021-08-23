# @Time     : 2021/5/30
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from abc import ABCMeta, abstractmethod
from operator import not_
from typing import Optional

from ..components.conf import IConfig
from ..components.event_hook import AbstractEventHooksManager
from .client import IAsyncHttpClient, AsyncHttpClient
from .manager import AsyncHttpClientManager


class IAsyncHttpClientFactory(metaclass=ABCMeta):

    @abstractmethod
    def create(self) -> IAsyncHttpClient:
        pass


class AsyncHttpClientFactory(IAsyncHttpClientFactory):
    manager = AsyncHttpClientManager()

    def __init__(self,
                 node: str,
                 config: Optional[IConfig] = None,
                 hooks: Optional[AbstractEventHooksManager] = None):
        self._node = node
        self._config = config
        self._hooks = hooks

    def create(self) -> IAsyncHttpClient:
        instance = AsyncHttpClientFactory.manager.get(self._node)
        if not_(instance):
            instance = AsyncHttpClient(self._config, self._hooks)
            AsyncHttpClientFactory.manager.set(self._node, instance)
        return instance
