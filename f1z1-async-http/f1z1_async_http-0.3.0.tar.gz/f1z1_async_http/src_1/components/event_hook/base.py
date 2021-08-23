# @Time     : 2021/7/18
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from abc import abstractmethod
from typing import Callable, Iterable, TypeVar, Union

T = TypeVar("T")


class IAsyncEventHook(object):
    """
    event hook interface
    """

    @abstractmethod
    async def trigger(self, message: T):
        raise NotImplementedError()

AsyncFunction = Callable
HookOrAFunc = Union[AsyncFunction, IAsyncEventHook]


class IAsyncEventHooks(object):
    """
    event hooks interface
    """

    @abstractmethod
    def register(self, hook_or_afunc: HookOrAFunc) -> int:
        """
        注册
        :param hook_or_afunc:
        :return:
        """
        raise NotImplementedError()

    def unregister(self, hook_or_afunc: HookOrAFunc) -> int:
        """
        移除
        :param hook_or_afunc:
        :return:
        """
        raise NotImplementedError()

    def __iter__(self) -> Iterable[HookOrAFunc]:
        raise NotImplementedError()
