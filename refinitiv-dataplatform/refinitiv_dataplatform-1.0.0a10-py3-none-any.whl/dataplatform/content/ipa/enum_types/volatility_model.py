# coding: utf8
# contract_gen 2020-05-18 08:30:59.232841

__all__ = ["VolatilityModel"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class VolatilityModel(Enum):
    CUBIC_SPLINE = "CubicSpline"
    SABR = "SABR"
    SVI = "SVI"
    TWIN_LOGNORMAL = "TwinLognormal"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(VolatilityModel, _VOLATILITY_MODEL_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_VOLATILITY_MODEL_VALUES_IN_LOWER_BY_VOLATILITY_MODEL, some)


_VOLATILITY_MODEL_VALUES = tuple(t.value for t in VolatilityModel)
_VOLATILITY_MODEL_VALUES_IN_LOWER_BY_VOLATILITY_MODEL = {
    name.lower(): item for name, item in VolatilityModel.__members__.items()
}
