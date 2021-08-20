# coding: utf8
# contract_gen 2020-05-18 08:30:59.217815

__all__ = ["AverageType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class AverageType(Enum):
    ARITHMETIC_RATE = "ArithmeticRate"
    ARITHMETIC_STRIKE = "ArithmeticStrike"
    GEOMETRIC_RATE = "GeometricRate"
    GEOMETRIC_STRIKE = "GeometricStrike"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(AverageType, _AVERAGE_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_AVERAGE_TYPE_VALUES_IN_LOWER_BY_AVERAGE_TYPE, some)


_AVERAGE_TYPE_VALUES = tuple(t.value for t in AverageType)
_AVERAGE_TYPE_VALUES_IN_LOWER_BY_AVERAGE_TYPE = {
    name.lower(): item for name, item in AverageType.__members__.items()
}
