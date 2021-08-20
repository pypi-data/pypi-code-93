# coding: utf8
# contract_gen 2020-05-18 08:30:59.214815

__all__ = ["CdsConvention"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class CdsConvention(Enum):
    ISDA = "ISDA"
    USER_DEFINED = "UserDefined"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(CdsConvention, _CDS_CONVENTION_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_CDS_CONVENTION_VALUES_IN_LOWER_BY_CDS_CONVENTION, some)


_CDS_CONVENTION_VALUES = tuple(t.value for t in CdsConvention)
_CDS_CONVENTION_VALUES_IN_LOWER_BY_CDS_CONVENTION = {
    name.lower(): item for name, item in CdsConvention.__members__.items()
}
