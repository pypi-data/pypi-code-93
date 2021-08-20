# coding: utf8
# contract_gen 2020-06-16 10:26:10.697158

__all__ = ["UnderlyingType"]

from enum import Enum, unique

from .common_tools import _convert_to_str, _normalize


@unique
class UnderlyingType(Enum):
    CAP = "Cap"
    ETI = "Eti"
    FX = "Fx"
    SWAPTION = "Swaption"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(UnderlyingType, _UNDERLYING_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_UNDERLYING_TYPE_VALUES_IN_LOWER_BY_UNDERLYING_TYPE, some)


_UNDERLYING_TYPE_VALUES = tuple(t.value for t in UnderlyingType)
_UNDERLYING_TYPE_VALUES_IN_LOWER_BY_UNDERLYING_TYPE = {
    name.lower(): item for name, item in UnderlyingType.__members__.items()
}
