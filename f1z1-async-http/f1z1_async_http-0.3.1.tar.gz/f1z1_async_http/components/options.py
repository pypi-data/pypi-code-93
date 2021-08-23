# @Time     : 2021/8/20
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from abc import abstractmethod
from collections import defaultdict, OrderedDict
from operator import not_
from typing import Dict, Optional

DictOrNone = Optional[Dict]


class IOptions:

    @abstractmethod
    def as_dict(self) -> DictOrNone:
        pass


class Option(IOptions):

    def __init__(self):
        self._ordered = OrderedDict()

    def empty(self):
        return not_(self._ordered)

    def clear(self):
        self._ordered.clear()

    def get(self, key, default=None):
        return self._ordered.get(key, default)

    def update(self, options: Dict) -> None:
        dict_ = self._to_dict(options)
        if not_(dict_):
            return
        self._ordered.update(dict_)

    def as_dict(self) -> DictOrNone:
        if self.empty():
            return None
        return {key: self.get(key) for key in self._ordered}

    def _to_dict(self, value) -> Dict:
        if isinstance(value, IOptions):
            return value.as_dict()
        return value

    def __setitem__(self, key, value):
        self._ordered[key] = value

    def __getitem__(self, key):
        return self._ordered[key]

    def __del__(self):
        del self._ordered

    def __str__(self):
        return f"{self.__class__.__name__}(options={self.as_dict()})"


class Options(IOptions):
    __slots__ = ["_options"]

    def __init__(self):
        self._options = defaultdict(lambda: self.factory())

    def empty(self) -> bool:
        return not_(self._options)

    def clear(self) -> None:
        self._options.clear()

    def update(self, key: str, options: Dict):
        self.get(key).update(options)
        return self

    def get(self, key: str) -> Option:
        return self._options[key]

    def as_dict(self) -> DictOrNone:
        if self.empty():
            return None
        return {key: self.get(key).as_dict() for key in self._options}

    def factory(self):
        return Option()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(options={self.as_dict()})"

    def __del__(self):
        del self._options
