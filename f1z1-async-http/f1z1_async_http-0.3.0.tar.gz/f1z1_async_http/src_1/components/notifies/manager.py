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
from typing import Callable, Dict, List

from ..event_hook import AbstractEventHooksManager
from .base import IAsyncNotifier
from .notifier import AsyncRequestNotifier, AsyncResponseNotifier, Notifier
from .rmq import IRequestMessage, RequestMessageQueue


class IAsyncNotifierManager(metaclass=ABCMeta):

    @property
    def completed(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def as_dict(self) -> Dict[str, List[Callable]]:
        raise NotImplementedError()


class AsyncNotifierManager(IAsyncNotifierManager):
    """
    通知管理器
    """

    def __init__(self, hooks: AbstractEventHooksManager):
        self._hooks = hooks
        self._messages = RequestMessageQueue(2 ** 31)

    @property
    def completed(self) -> bool:
        return self._messages.empty()

    def request(self, message: IRequestMessage):
        hooks = self._hooks.get("request")
        return [
            self.notify(
                AsyncRequestNotifier(Notifier(hooks), message)
            )
        ]

    def response(self, message: IRequestMessage):
        hooks = self._hooks.get("response")
        return [
            self.notify(AsyncResponseNotifier(Notifier(hooks), message))
        ]

    def notify(self, notifier: IAsyncNotifier):
        async def execute(value):
            return await notifier.notify(value)

        return execute

    def as_dict(self):
        message = self._messages
        return {
            "request": self.request(message),
            "response": self.response(message)
        }

    def __str__(self):
        return f"{self.__class__.__name__}(messages={self._messages}, hooks={self._hooks})"
