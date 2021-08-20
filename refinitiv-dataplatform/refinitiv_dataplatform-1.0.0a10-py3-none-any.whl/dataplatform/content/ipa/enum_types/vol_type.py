# coding: utf8
# contract_gen 2020-05-18 08:30:59.241817

__all__ = ["VolType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class VolType(Enum):
    CALL = "Call"
    PUT = "Put"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(VolType, _VOL_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_VOL_TYPE_VALUES_IN_LOWER_BY_VOL_TYPE, some)


_VOL_TYPE_VALUES = tuple(t.value for t in VolType)
_VOL_TYPE_VALUES_IN_LOWER_BY_VOL_TYPE = {
    name.lower(): item for name, item in VolType.__members__.items()
}
