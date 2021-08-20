# coding: utf8
# contract_gen 2020-06-15 10:07:47.554306

__all__ = ["InterpolationMode"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class InterpolationMode(Enum):
    CUBIC_DISCOUNT = "CubicDiscount"
    CUBIC_RATE = "CubicRate"
    CUBIC_SPLINE = "CubicSpline"
    FORWARD_MONOTONE_CONVEX = "ForwardMonotoneConvex"
    LINEAR = "Linear"
    LOG = "Log"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(InterpolationMode, _INTERPOLATION_MODE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(
            _INTERPOLATION_MODE_VALUES_IN_LOWER_BY_INTERPOLATION_MODE, some
        )


_INTERPOLATION_MODE_VALUES = tuple(t.value for t in InterpolationMode)
_INTERPOLATION_MODE_VALUES_IN_LOWER_BY_INTERPOLATION_MODE = {
    name.lower(): item for name, item in InterpolationMode.__members__.items()
}
