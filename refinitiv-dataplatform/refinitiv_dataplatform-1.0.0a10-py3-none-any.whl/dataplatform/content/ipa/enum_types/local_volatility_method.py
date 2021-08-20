# coding: utf8
# contract_gen 2020-05-18 08:30:59.240817

__all__ = ["LocalVolatilityMethod"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class LocalVolatilityMethod(Enum):
    BEST_SMILE = "BestSmile"
    CONVEX_SMILE = "ConvexSmile"
    PARABOLA_SMOOTH = "ParabolaSmooth"
    PARABOLA_WITHOUT_EXTRAPOL = "ParabolaWithoutExtrapol"
    RATIONAL_SMOOTH = "RationalSmooth"
    RATIONAL_WITHOUT_EXTRAPOL = "RationalWithoutExtrapol"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            LocalVolatilityMethod, _LOCAL_VOLATILITY_METHOD_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _LOCAL_VOLATILITY_METHOD_VALUES_IN_LOWER_BY_LOCAL_VOLATILITY_METHOD, some
        )


_LOCAL_VOLATILITY_METHOD_VALUES = tuple(t.value for t in LocalVolatilityMethod)
_LOCAL_VOLATILITY_METHOD_VALUES_IN_LOWER_BY_LOCAL_VOLATILITY_METHOD = {
    name.lower(): item for name, item in LocalVolatilityMethod.__members__.items()
}
