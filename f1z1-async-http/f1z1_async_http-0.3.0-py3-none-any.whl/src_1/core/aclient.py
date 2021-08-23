# @Time     : 2021/7/18
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from typing import AnyStr, Union

from httpx import AsyncClient, Limits, Timeout, URL
from f1z1_common.src.is_ import is_validate

IntOrFloat = Union[int, float]


class IAsyncClientBuilder(object):

    def set_base_url(self, url: AnyStr) -> ["IAsyncClientBuilder"]:
        raise NotImplementedError("")

    def set_event_hooks(self, hooks: dict) -> ["IAsyncClientBuilder"]:
        raise NotImplementedError("")

    def set_max_connection(self, max_connection: int) -> ["IAsyncClientBuilder"]:
        raise NotImplementedError("")

    def set_max_keepalive(self, max_keepalive: int) -> ["IAsyncClientBuilder"]:
        raise NotImplementedError("")

    def set_timeout(self, timeout: IntOrFloat) -> ["IAsyncClientBuilder"]:
        raise NotImplementedError("")

    def build(self) -> AsyncClient:
        raise NotImplementedError()


class AsyncClientBuilder(IAsyncClientBuilder):

    def __init__(self):
        self._base_url: AnyStr = ""
        self._max_connection: int = 100
        self._max_keepalive: int = 20
        self._timeout: IntOrFloat = 3600
        self._event_hooks: dict = None

    def set_base_url(self, url: AnyStr):
        if self._is_any_string(url):
            self._base_url = url
        return self

    def set_event_hooks(self, hooks: dict):
        if is_validate.is_dict(hooks):
            self._event_hooks = hooks
        return self

    def set_max_connection(self, max_connection: int):
        if self._is_int(max_connection):
            self._max_connection = abs(max_connection)
        return self

    def set_max_keepalive(self, max_keepalive: int):
        if self._is_int(max_keepalive):
            self._max_keepalive = abs(max_keepalive)
        return self

    def set_timeout(self, timeout: IntOrFloat):
        if self._is_int_or_float(timeout):
            self._timeout = timeout
        return self

    def build(self):
        return AsyncClient(
            base_url=URL(self._base_url),
            event_hooks=self._event_hooks,
            limits=Limits(max_connections=self._max_connection, max_keepalive_connections=self._max_keepalive),
            timeout=Timeout(self._timeout)
        )

    def _is_any_string(self, value):
        return is_validate.is_any_string(value)

    def _is_int(self, value):
        return is_validate.is_number(value)

    def _is_int_or_float(self, value):
        return is_validate.is_number(value)
