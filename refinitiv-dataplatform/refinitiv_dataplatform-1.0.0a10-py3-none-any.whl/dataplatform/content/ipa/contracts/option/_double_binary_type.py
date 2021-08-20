# coding: utf8

__all__ = ["DoubleBinaryType"]

from enum import Enum, unique
from refinitiv.dataplatform.content.ipa.enum_types.common_tools import (
    _convert_to_str,
    _normalize,
)


@unique
class DoubleBinaryType(Enum):
    NONE = "None"
    DOUBLE_NO_TOUCH = "DoubleNoTouch"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(DoubleBinaryType, _DOUBLE_BINARY_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(
            _DOUBLE_BINARY_TYPE_VALUES_IN_LOWER_BY_DOUBLE_BINARY_TYPE, some
        )


_DOUBLE_BINARY_TYPE_VALUES = (t.value for t in DoubleBinaryType)
_DOUBLE_BINARY_TYPE_VALUES_IN_LOWER_BY_DOUBLE_BINARY_TYPE = {
    name.lower(): item for name, item in DoubleBinaryType.__members__.items()
}
