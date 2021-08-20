# coding: utf8

__all__ = ["UnderlyingType"]

from enum import Enum, unique
from refinitiv.dataplatform.content.ipa.enum_types.common_tools import (
    _convert_to_str,
    _normalize,
)


class UnderlyingType(Enum):
    """
    Underlying type of the option.
    Possible values:
        - Eti
        - Fx
    """

    ETI = "Eti"
    FX = "Fx"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(UnderlyingType, _UNDERLYING_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_UNDERLYING_TYPE_VALUES_IN_LOWER_BY_YIELD_TYPE, some)


_UNDERLYING_TYPE_VALUES = (t.value for t in UnderlyingType)
_UNDERLYING_TYPE_VALUES_IN_LOWER_BY_YIELD_TYPE = {
    name.lower(): item for name, item in UnderlyingType.__members__.items()
}
