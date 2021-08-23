# @Time     : 2021/7/18
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from collections import defaultdict, OrderedDict
from typing import Dict, DefaultDict, Optional

from .base import IRequestOptions


class IOption(object):

    def set(self, key, value) -> None:
        raise NotImplementedError("")

    def get(self, key, default=None):
        raise NotImplementedError("")

    def as_dict(self) -> Optional[Dict]:
        raise NotImplementedError("")


class Option(IOption):

    def __init__(self):
        self._option = OrderedDict()

    def empty(self):
        return not self._option

    def get(self, key, default=None):
        return self._option.get(key, default)

    def set(self, key, value) -> None:
        self[key] = value

    def as_dict(self):
        if self.empty():
            return None
        return {key: value for key, value in self._option.items()}

    def __setitem__(self, key, value):
        self._option[key] = value

    def __getitem__(self, key):
        return self._option[key]

    def __del__(self):
        del self._option


class RequestOptions(IRequestOptions):
    __slots__ = ["_options"]

    def __init__(self):
        self._options: DefaultDict[str, IOption] = defaultdict(Option)

    def add_cookies(self, key, value):
        self._set("cookies", key, value)

    def add_data(self, key, value):
        self._set("data", key, value)

    def add_headers(self, key, value):
        self._set("headers", key, value)

    def add_json(self, key, value):
        self._set("json", key, value)

    def add_params(self, key, value):
        self._set("params", key, value)

    def as_dict(self):
        if self.empty():
            return {}
        return {
            key: item.as_dict()
            for key, item in self._options.items()
        }

    def empty(self):
        return not self._options

    def _set(self, option: str, key, value):
        self[option].set(key, value)

    def __getitem__(self, key) -> IOption:
        return self._options[key]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(options={self._options.keys()})"
