# coding: utf8
# contract_gen 2020-05-18 08:30:59.249849

__all__ = ["DiscountingType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class DiscountingType(Enum):
    LIBOR_DISCOUNTING = "LiborDiscounting"
    OIS_DISCOUNTING = "OisDiscounting"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(DiscountingType, _DISCOUNTING_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_DISCOUNTING_TYPE_VALUES_IN_LOWER_BY_DISCOUNTING_TYPE, some)


_DISCOUNTING_TYPE_VALUES = tuple(t.value for t in DiscountingType)
_DISCOUNTING_TYPE_VALUES_IN_LOWER_BY_DISCOUNTING_TYPE = {
    name.lower(): item for name, item in DiscountingType.__members__.items()
}
