# coding: utf8
# contract_gen 2020-05-18 08:30:59.221841

__all__ = ["BinaryType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class BinaryType(Enum):
    DIGITAL = "Digital"
    NO_TOUCH = "NoTouch"
    NONE = "None"
    ONE_TOUCH = "OneTouch"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(BinaryType, _BINARY_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_BINARY_TYPE_VALUES_IN_LOWER_BY_BINARY_TYPE, some)


_BINARY_TYPE_VALUES = tuple(t.value for t in BinaryType)
_BINARY_TYPE_VALUES_IN_LOWER_BY_BINARY_TYPE = {
    name.lower(): item for name, item in BinaryType.__members__.items()
}
