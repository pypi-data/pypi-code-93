# coding: utf8
# contract_gen 2020-05-18 08:30:59.205820

__all__ = ["InterestType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class InterestType(Enum):
    FIXED = "Fixed"
    FLOAT = "Float"
    STEPPED = "Stepped"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(InterestType, _INTEREST_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_INTEREST_TYPE_VALUES_IN_LOWER_BY_INTEREST_TYPE, some)


_INTEREST_TYPE_VALUES = tuple(t.value for t in InterestType)
_INTEREST_TYPE_VALUES_IN_LOWER_BY_INTEREST_TYPE = {
    name.lower(): item for name, item in InterestType.__members__.items()
}
