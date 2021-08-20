# coding: utf8
# contract_gen 2020-06-16 10:26:10.695191

__all__ = ["VolatilityAdjustmentType"]

from enum import Enum, unique

from .common_tools import _convert_to_str, _normalize


@unique
class VolatilityAdjustmentType(Enum):
    CONSTANT_CAP = "ConstantCap"
    CONSTANT_CAPLET = "ConstantCaplet"
    NORMALIZED_CAP = "NormalizedCap"
    NORMALIZED_CAPLET = "NormalizedCaplet"
    PB_UNDEFINED = "PbUndefined"
    SHIFTED_CAP = "ShiftedCap"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            VolatilityAdjustmentType, _VOLATILITY_ADJUSTMENT_TYPE_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _VOLATILITY_ADJUSTMENT_TYPE_VALUES_IN_LOWER_BY_VOLATILITY_ADJUSTMENT_TYPE,
            some,
        )


_VOLATILITY_ADJUSTMENT_TYPE_VALUES = tuple(t.value for t in VolatilityAdjustmentType)
_VOLATILITY_ADJUSTMENT_TYPE_VALUES_IN_LOWER_BY_VOLATILITY_ADJUSTMENT_TYPE = {
    name.lower(): item for name, item in VolatilityAdjustmentType.__members__.items()
}
