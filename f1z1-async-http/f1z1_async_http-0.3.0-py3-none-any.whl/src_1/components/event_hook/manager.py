# @Time     : 2021/7/18
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
try:
    import simplejson as json
except ImportError:
    import json

from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import Dict, DefaultDict

from .base import IAsyncEventHooks, HookOrAFunc
from .hooks import AsyncEventHookList, AsyncFunctionHooks, AsyncEventHooks

HooksManager = DefaultDict[str, IAsyncEventHooks]


class AbstractEventHooksManager(metaclass=ABCMeta):
    HOOK_KEY = ["request", "response"]
    __slots__ = ["_manager"]

    def __init__(self):
        self._manager: HooksManager = defaultdict(self._factory)

    def set(self, key: str, hook_or_afunc: HookOrAFunc) -> None:
        self[key] = hook_or_afunc

    def get(self, key: str) -> IAsyncEventHooks:
        return self[key]

    def clear(self):
        if not self.empty():
            self._manager.clear()

    def empty(self):
        return not self._manager

    def as_dict(self) -> Dict[str, IAsyncEventHooks]:
        return {k: self[k] for k in AbstractEventHooksManager.HOOK_KEY}

    @abstractmethod
    def _factory(self) -> IAsyncEventHooks:
        raise NotImplementedError()

    def __setitem__(self, key: str, value: HookOrAFunc):
        self[key].register(value)

    def __getitem__(self, key: str):
        return self._manager[key]

    def __str__(self):
        return f"{self.__class__.__name__}(manager={self._manager.keys()})"


class FunctionHooksManager(AbstractEventHooksManager):

    def _factory(self):
        return AsyncFunctionHooks(AsyncEventHookList())


class EventHooksManager(AbstractEventHooksManager):

    def _factory(self):
        return AsyncEventHooks(AsyncEventHookList())
