# coding: utf8
# contract_gen 2020-06-15 10:07:47.552306

__all__ = ["ExtrapolationMode"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class ExtrapolationMode(Enum):
    CONSTANT = "Constant"
    LINEAR = "Linear"
    NONE = "None"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(ExtrapolationMode, _EXTRAPOLATION_MODE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(
            _EXTRAPOLATION_MODE_VALUES_IN_LOWER_BY_EXTRAPOLATION_MODE, some
        )


_EXTRAPOLATION_MODE_VALUES = tuple(t.value for t in ExtrapolationMode)
_EXTRAPOLATION_MODE_VALUES_IN_LOWER_BY_EXTRAPOLATION_MODE = {
    name.lower(): item for name, item in ExtrapolationMode.__members__.items()
}
