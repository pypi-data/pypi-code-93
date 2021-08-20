# coding: utf8
# contract_gen 2020-05-18 08:30:59.219828

__all__ = ["UpOrDown"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class UpOrDown(Enum):
    DOWN = "Down"
    UP = "Up"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(UpOrDown, _UP_OR_DOWN_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_UP_OR_DOWN_VALUES_IN_LOWER_BY_UP_OR_DOWN, some)


_UP_OR_DOWN_VALUES = tuple(t.value for t in UpOrDown)
_UP_OR_DOWN_VALUES_IN_LOWER_BY_UP_OR_DOWN = {
    name.lower(): item for name, item in UpOrDown.__members__.items()
}
