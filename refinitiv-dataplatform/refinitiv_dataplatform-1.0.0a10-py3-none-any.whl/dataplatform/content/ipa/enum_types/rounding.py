# coding: utf8
# contract_gen 2020-05-18 08:30:59.211843

__all__ = ["Rounding"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class Rounding(Enum):
    DEFAULT = "Default"
    EIGHT = "Eight"
    FIVE = "Five"
    FOUR = "Four"
    ONE = "One"
    SEVEN = "Seven"
    SIX = "Six"
    THREE = "Three"
    TWO = "Two"
    UNROUNDED = "Unrounded"
    ZERO = "Zero"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(Rounding, _ROUNDING_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_ROUNDING_VALUES_IN_LOWER_BY_ROUNDING, some)


_ROUNDING_VALUES = tuple(t.value for t in Rounding)
_ROUNDING_VALUES_IN_LOWER_BY_ROUNDING = {
    name.lower(): item for name, item in Rounding.__members__.items()
}
