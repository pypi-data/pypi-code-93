# @Time     : 2021/8/20
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from abc import abstractmethod
from collections import defaultdict
from operator import not_
from typing import Callable, Iterable, NoReturn

from f1z1_common.src import afunc_manager
from f1z1_common.src.callback import AbstractCallbackManager

AFunc = Callable
AFuncs = Iterable[AFunc]
AFuncManager = AbstractCallbackManager


class Hook:

    @property
    @abstractmethod
    def request(self) -> AFuncs:
        pass

    @property
    @abstractmethod
    def response(self) -> AFuncs:
        pass


class EventHook(Hook):
    __slots__ = "_event_hooks"

    def __init__(self, manager: AFuncManager = None):
        self._event_hooks = defaultdict(lambda: self.factory(manager))

    @property
    def request(self):
        return self.to_list("request")

    @property
    def response(self):
        return self.to_list("response")

    def register(self, key: str, afunc: AFunc) -> NoReturn:
        self.get(key).add(afunc)

    def unregister(self, key: str, afunc: AFunc) -> None:
        self.get(key).remove(afunc)

    def factory(self, manager: AFuncManager = None):
        _afunc_manager = afunc_manager()
        if manager:
            _afunc_manager.manager = manager
        return _afunc_manager

    def get(self, key: str):
        return self._event_hooks[key]

    def to_list(self, key: str):
        if self.empty():
            return []
        return [hook for hook in self.get(key)]

    def clear(self):
        self._event_hooks.clear()

    def empty(self):
        return not_(self._event_hooks)

    def __str__(self):
        return f"{self.__class__.__name__}(request={self.request}, response={self.response})"

    def __del__(self):
        del self._event_hooks
