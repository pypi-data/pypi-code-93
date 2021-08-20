# coding: utf8
# contract_gen 2020-06-16 10:26:10.708191

__all__ = ["FxVolatilityModel"]

from enum import Enum, unique

from .common_tools import _convert_to_str, _normalize


@unique
class FxVolatilityModel(Enum):
    CUBIC_SPLINE = "CubicSpline"
    SABR = "SABR"
    SVI = "SVI"
    TWIN_LOGNORMAL = "TwinLognormal"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(FxVolatilityModel, _FX_VOLATILITY_MODEL_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(
            _FX_VOLATILITY_MODEL_VALUES_IN_LOWER_BY_FX_VOLATILITY_MODEL, some
        )


_FX_VOLATILITY_MODEL_VALUES = tuple(t.value for t in FxVolatilityModel)
_FX_VOLATILITY_MODEL_VALUES_IN_LOWER_BY_FX_VOLATILITY_MODEL = {
    name.lower(): item for name, item in FxVolatilityModel.__members__.items()
}
