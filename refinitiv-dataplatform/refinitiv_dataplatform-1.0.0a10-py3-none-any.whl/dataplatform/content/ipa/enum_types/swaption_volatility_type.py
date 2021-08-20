# coding: utf8
# contract_gen 2020-05-18 08:30:59.250817

__all__ = ["SwaptionVolatilityType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class SwaptionVolatilityType(Enum):
    ATM_SURFACE = "AtmSurface"
    SABR_VOLATILITY_CUBE = "SabrVolatilityCube"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            SwaptionVolatilityType, _SWAPTION_VOLATILITY_TYPE_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _SWAPTION_VOLATILITY_TYPE_VALUES_IN_LOWER_BY_SWAPTION_VOLATILITY_TYPE, some
        )


_SWAPTION_VOLATILITY_TYPE_VALUES = tuple(t.value for t in SwaptionVolatilityType)
_SWAPTION_VOLATILITY_TYPE_VALUES_IN_LOWER_BY_SWAPTION_VOLATILITY_TYPE = {
    name.lower(): item for name, item in SwaptionVolatilityType.__members__.items()
}
