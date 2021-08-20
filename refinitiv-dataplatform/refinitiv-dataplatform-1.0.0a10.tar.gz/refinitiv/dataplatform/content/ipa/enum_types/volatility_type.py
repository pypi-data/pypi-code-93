# coding: utf8
# contract_gen 2020-05-18 08:30:59.233816

__all__ = ["VolatilityType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class VolatilityType(Enum):
    IMPLIED = "Implied"
    SVI_SURFACE = "SVISurface"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(VolatilityType, _VOLATILITY_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_VOLATILITY_TYPE_VALUES_IN_LOWER_BY_VOLATILITY_TYPE, some)


_VOLATILITY_TYPE_VALUES = tuple(t.value for t in VolatilityType)
_VOLATILITY_TYPE_VALUES_IN_LOWER_BY_VOLATILITY_TYPE = {
    name.lower(): item for name, item in VolatilityType.__members__.items()
}
