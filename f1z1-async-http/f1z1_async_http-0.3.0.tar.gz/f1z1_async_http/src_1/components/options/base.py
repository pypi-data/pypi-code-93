# @Time     : 2021/7/18
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from abc import ABCMeta, abstractmethod
from typing import Any, Dict


class IRequestOptions(metaclass=ABCMeta):

    @abstractmethod
    def add_cookies(self, key, value):
        pass

    @abstractmethod
    def add_data(self, key, value):
        pass

    @abstractmethod
    def add_headers(self, key, value):
        pass

    @abstractmethod
    def add_json(self, key, value):
        pass

    @abstractmethod
    def add_params(self, key, value):
        pass

    @abstractmethod
    def as_dict(self) -> Dict[str, Any]:
        pass
