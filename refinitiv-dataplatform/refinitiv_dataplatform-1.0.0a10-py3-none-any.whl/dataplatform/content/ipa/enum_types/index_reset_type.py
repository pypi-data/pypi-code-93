# coding: utf8
# contract_gen 2020-05-18 08:30:59.245816

__all__ = ["IndexResetType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class IndexResetType(Enum):
    IN_ADVANCE = "InAdvance"
    IN_ARREARS = "InArrears"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(IndexResetType, _INDEX_RESET_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_INDEX_RESET_TYPE_VALUES_IN_LOWER_BY_INDEX_RESET_TYPE, some)


_INDEX_RESET_TYPE_VALUES = tuple(t.value for t in IndexResetType)
_INDEX_RESET_TYPE_VALUES_IN_LOWER_BY_INDEX_RESET_TYPE = {
    name.lower(): item for name, item in IndexResetType.__members__.items()
}
