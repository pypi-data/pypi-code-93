# coding: utf8

__all__ = ["FxBinaryType"]

from enum import unique

from refinitiv.dataplatform.content.ipa.enum_types.common_tools import (
    _convert_to_str,
    _normalize,
)
from ._abstracted_class import BinaryType


@unique
class FxBinaryType(BinaryType):
    NONE = "None"
    ONE_TOUCH_IMMEDIATE = "OneTouchImmediate"
    ONE_TOUCH_DEFERRED = "OneTouchDeferred"
    NO_TOUCH = "NoTouch"
    DIGITAL = "Digital"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(FxBinaryType, _FX_BINARY_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_FX_BINARY_TYPE_VALUES_IN_LOWER_BY_BINARY_TYPE, some)


_FX_BINARY_TYPE_VALUES = (t.value for t in FxBinaryType)
_FX_BINARY_TYPE_VALUES_IN_LOWER_BY_BINARY_TYPE = {
    name.lower(): item for name, item in FxBinaryType.__members__.items()
}
