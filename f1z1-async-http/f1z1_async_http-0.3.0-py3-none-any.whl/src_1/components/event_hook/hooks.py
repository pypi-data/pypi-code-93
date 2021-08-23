# @Time     : 2021/7/18
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from f1z1_common.src import check_async_function, afunc_manager

from .base import IAsyncEventHook, IAsyncEventHooks, AsyncFunction, HookOrAFunc


class AsyncEventHookList(IAsyncEventHooks):
    __slots__ = ["_list"]

    def __init__(self):
        self._list = []

    @property
    def length(self):
        return len(self._list)

    def register(self, hook_or_afunc: HookOrAFunc) -> int:
        if not self._is_exists(hook_or_afunc):
            self._list.append(hook_or_afunc)
        return self.length

    def unregister(self, hook_or_afunc: HookOrAFunc) -> int:
        idx = self._find(hook_or_afunc)
        if idx > -1:
            self._list.pop(idx)

        return self.length

    def _is_exists(self, value) -> bool:
        return value in self._list

    def _find(self, value) -> int:
        if not self._is_exists(value):
            return -1
        return -1 if not self._is_exists(value) else self._list.index(value)

    def __iter__(self):
        if self.length:
            for item in self._list:
                yield item

    def __str__(self):
        return f"{self.__class__.__name__}(list={str(self._list)}, size={self.length})"


class AsyncEventHooksDecorate(IAsyncEventHooks):

    def __init__(self, event_hooks: IAsyncEventHooks):
        self._event_hooks = event_hooks

    def register(self, hook_or_afunc: HookOrAFunc) -> int:
        return self._event_hooks.register(hook_or_afunc)

    def unregister(self, hook_or_afunc: HookOrAFunc) -> int:
        return self._event_hooks.unregister(hook_or_afunc)

    def __iter__(self):
        for item in self._event_hooks:
            yield item

    def __str__(self):
        return f"{self.__class__.__name__}(event_hooks={str(self._event_hooks)})"


class AsyncFunctionHooks(AsyncEventHooksDecorate):

    def __init__(self, event_hooks: IAsyncEventHooks):
        super().__init__(event_hooks)

    def register(self, afunc: AsyncFunction) -> int:
        self._check(afunc)
        return super().register(afunc)

    def _check(self, value):
        return check_async_function(value)


class AsyncEventHooks(AsyncEventHooksDecorate):

    def __init__(self, event_hooks: IAsyncEventHooks):
        super().__init__(event_hooks)

    def register(self, hook: IAsyncEventHook) -> int:
        self._check(hook)
        return super().register(hook)

    def _check(self, value):
        if not isinstance(value, IAsyncEventHook):
            raise ValueError(
                f"value need IAsyncEventHook, but got {type(value).__name__}"
            )
