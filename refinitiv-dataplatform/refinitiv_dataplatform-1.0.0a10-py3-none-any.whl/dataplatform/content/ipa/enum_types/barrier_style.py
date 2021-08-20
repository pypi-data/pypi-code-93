# coding: utf8
# contract_gen 2020-09-02 06:21:29.316954

__all__ = ["BarrierStyle"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class BarrierStyle(Enum):
    NONE = "None"
    AMERICAN = "American"
    EUROPEAN = "European"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(BarrierStyle, _BARRIER_STYLE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_BARRIER_STYLE_VALUES_IN_LOWER_BY_BARRIER_STYLE, some)


_BARRIER_STYLE_VALUES = tuple(t.value for t in BarrierStyle)
_BARRIER_STYLE_VALUES_IN_LOWER_BY_BARRIER_STYLE = {
    name.lower(): item for name, item in BarrierStyle.__members__.items()
}
