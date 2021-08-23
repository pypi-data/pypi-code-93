# @Time     : 2021/6/1
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from typing import Optional

from .client import IAsyncHttpClient


class IAsyncHttpClientManager(object):

    def set(self, node, instance: IAsyncHttpClient):
        raise NotImplementedError("")

    def get(self, node) -> Optional[IAsyncHttpClient]:
        raise NotImplementedError("")

    def remove(self, node) -> None:
        raise NotImplementedError("")

    def clear(self) -> None:
        raise NotImplementedError("")


class AsyncHttpClientManager(IAsyncHttpClientManager):
    __shared = {}  # shared states

    def __init__(self):
        self.__dict__ = AsyncHttpClientManager.__shared

    def set(self, node, instance):
        if not self._is_client(instance):
            raise ValueError(
                f"instance need IAsyncHttpClient, but got {type(instance).__name__}"
            )
        setattr(self, node, instance)

    def get(self, node):
        return getattr(self, node, None)

    def remove(self, node) -> None:
        delattr(self, node)

    def clear(self) -> None:
        AsyncHttpClientManager.__shared.clear()

    def _is_client(self, value):
        return isinstance(value, IAsyncHttpClient)
