# @Time     : 2021/8/9
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from abc import ABCMeta, abstractmethod
from collections import deque
from typing import Deque, Iterable, Optional, TypeVar

from httpx import Request

T = TypeVar("T")
RMQ = Deque[Request]


class IRequestMessage(metaclass=ABCMeta):

    @abstractmethod
    def empty(self):
        pass

    @abstractmethod
    def add(self, message: T) -> None:
        """
        添加消息
        :param message:
        :return:
        """
        pass

    @abstractmethod
    def pop(self) -> T:
        """
        移除消息
        :return:
        """
        pass


class RequestMessageQueue(IRequestMessage):

    def __init__(self, maxsize: int = None):
        self._messages: RMQ = deque(maxlen=maxsize)

    def empty(self):
        return not len(self._messages)

    def add(self, message: Request) -> None:
        self._messages.append(message)

    def pop(self) -> Optional[Request]:
        if self.empty():
            return None
        return self._messages.popleft()

    def __iter__(self) -> Iterable[Request]:
        while True:
            if self.empty():
                break
            yield self.pop()

    def __str__(self):
        return f"{self.__class__.__name__}(queue={str(self._messages)})"
