# coding: utf8
# contract_gen 2020-06-16 10:26:10.698160

__all__ = ["EtiInputVolatilityType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class EtiInputVolatilityType(Enum):
    IMPLIED = "Implied"
    QUOTED = "Quoted"
    SETTLE = "Settle"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            EtiInputVolatilityType, _ETI_INPUT_VOLATILITY_TYPE_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _ETI_INPUT_VOLATILITY_TYPE_VALUES_IN_LOWER_BY_ETI_INPUT_VOLATILITY_TYPE,
            some,
        )


_ETI_INPUT_VOLATILITY_TYPE_VALUES = tuple(t.value for t in EtiInputVolatilityType)
_ETI_INPUT_VOLATILITY_TYPE_VALUES_IN_LOWER_BY_ETI_INPUT_VOLATILITY_TYPE = {
    name.lower(): item for name, item in EtiInputVolatilityType.__members__.items()
}
