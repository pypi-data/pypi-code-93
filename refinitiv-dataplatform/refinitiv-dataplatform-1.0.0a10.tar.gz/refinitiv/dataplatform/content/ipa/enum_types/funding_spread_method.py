# coding: utf8
# contract_gen 2020-05-18 08:30:59.242815

__all__ = ["FundingSpreadMethod"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class FundingSpreadMethod(Enum):
    CDS_SPREAD = "CDSSpread"
    LIQUIDITY_SPREAD = "LiquiditySpread"
    PPZ_SPREAD = "PPZSpread"
    PARALLEL_CURVE_SHIFT = "ParallelCurveShift"
    RISKY_D_FS = "RiskyDFs"
    USE_CDS_SPREADS = "UseCDSSpreads"
    USE_Z_SPREAD = "UseZSpread"
    Z_SPREAD = "ZSpread"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(FundingSpreadMethod, _FUNDING_SPREAD_METHOD_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(
            _FUNDING_SPREAD_METHOD_VALUES_IN_LOWER_BY_FUNDING_SPREAD_METHOD, some
        )


_FUNDING_SPREAD_METHOD_VALUES = tuple(t.value for t in FundingSpreadMethod)
_FUNDING_SPREAD_METHOD_VALUES_IN_LOWER_BY_FUNDING_SPREAD_METHOD = {
    name.lower(): item for name, item in FundingSpreadMethod.__members__.items()
}
