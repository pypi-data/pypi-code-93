# coding: utf8
# contract_gen 2020-05-18 08:30:59.227815

__all__ = ["BarrierMode"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class BarrierMode(Enum):
    AMERICAN = "American"
    EARLY_END_WINDOW = "EarlyEndWindow"
    EUROPEAN = "European"
    FORWARD_START_WINDOW = "ForwardStartWindow"
    UNDEFINED = "Undefined"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(BarrierMode, _BARRIER_MODE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_BARRIER_MODE_VALUES_IN_LOWER_BY_BARRIER_MODE, some)


_BARRIER_MODE_VALUES = tuple(t.value for t in BarrierMode)
_BARRIER_MODE_VALUES_IN_LOWER_BY_BARRIER_MODE = {
    name.lower(): item for name, item in BarrierMode.__members__.items()
}
