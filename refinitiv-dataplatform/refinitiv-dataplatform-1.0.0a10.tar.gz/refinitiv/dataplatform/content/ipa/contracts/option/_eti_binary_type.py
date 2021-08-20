# coding: utf8

__all__ = ["EtiBinaryType"]

from enum import Enum, unique
from refinitiv.dataplatform.content.ipa.enum_types.common_tools import (
    _convert_to_str,
    _normalize,
)
from ._abstracted_class import BinaryType


@unique
class EtiBinaryType(BinaryType):
    NONE = "None"
    ONE_TOUCH = "OneTouch"
    NO_TOUCH = "NoTouch"
    DIGITAL = "Digital"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(EtiBinaryType, _ETI_BINARY_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_ETI_BINARY_TYPE_VALUES_IN_LOWER_BY_BINARY_TYPE, some)


_ETI_BINARY_TYPE_VALUES = (t.value for t in EtiBinaryType)
_ETI_BINARY_TYPE_VALUES_IN_LOWER_BY_BINARY_TYPE = {
    name.lower(): item for name, item in EtiBinaryType.__members__.items()
}
