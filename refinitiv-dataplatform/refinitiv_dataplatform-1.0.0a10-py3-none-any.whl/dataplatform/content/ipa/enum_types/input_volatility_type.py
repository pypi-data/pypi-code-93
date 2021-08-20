# coding: utf8
# contract_gen 2020-06-16 10:26:10.694191

__all__ = ["InputVolatilityType"]

from enum import Enum, unique

from .common_tools import _convert_to_str, _normalize


@unique
class InputVolatilityType(Enum):
    DEFAULT = "Default"
    LOG_NORMAL_VOLATILITY = "LogNormalVolatility"
    NORMALIZED_VOLATILITY = "NormalizedVolatility"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(InputVolatilityType, _INPUT_VOLATILITY_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(
            _INPUT_VOLATILITY_TYPE_VALUES_IN_LOWER_BY_INPUT_VOLATILITY_TYPE, some
        )


_INPUT_VOLATILITY_TYPE_VALUES = tuple(t.value for t in InputVolatilityType)
_INPUT_VOLATILITY_TYPE_VALUES_IN_LOWER_BY_INPUT_VOLATILITY_TYPE = {
    name.lower(): item for name, item in InputVolatilityType.__members__.items()
}
