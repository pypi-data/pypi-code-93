# @Time     : 2021/7/18
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from httpx import Request, Response
from f1z1_common.src.is_ import is_validate

from ..event_hook import IAsyncEventHooks
from .base import IAsyncNotifier
from .rmq import IRequestMessage


class Notifier(IAsyncNotifier):

    def __init__(self, hooks: IAsyncEventHooks):
        self._hooks = hooks

    async def notify(self, message) -> bool:
        if self._hooks_is_none():
            return True
        for fn in self._hooks:
            await fn(message)
        return True

    def _hooks_is_none(self):
        return is_validate.is_null(self._hooks)

    def __str__(self):
        return f"{self.__class__.__name__}(event_hooks={str(self._hooks)})"


class NotifierDecorate(IAsyncNotifier):

    def __init__(self, notifier: IAsyncNotifier):
        self._notifier = notifier

    async def notify(self, message) -> bool:
        return await self._notifier.notify(message)

    def __str__(self):
        return f"{self.__class__.__name__}(notifier={str(self._notifier)})"


class AsyncRequestNotifier(NotifierDecorate):

    def __init__(self, notifier: IAsyncNotifier, message: IRequestMessage):
        super().__init__(notifier)
        self._rm = message

    async def notify(self, request: Request) -> bool:
        self._rm.add(request)
        # print("add", self._rm)
        return await super().notify(request)


class AsyncResponseNotifier(NotifierDecorate):

    def __init__(self, notifier: IAsyncNotifier, message: IRequestMessage):
        super().__init__(notifier)
        self._rm = message

    async def notify(self, response: Response) -> bool:
        result = await super().notify(response)
        self._rm.pop()
        return result
