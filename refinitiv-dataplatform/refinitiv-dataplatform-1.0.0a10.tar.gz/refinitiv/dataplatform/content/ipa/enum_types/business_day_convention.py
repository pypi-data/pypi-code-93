# coding: utf8
# contract_gen 2020-05-18 08:30:59.206816

__all__ = ["BusinessDayConvention"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class BusinessDayConvention(Enum):
    BBSW_MODIFIED_FOLLOWING = "BbswModifiedFollowing"
    MODIFIED_FOLLOWING = "ModifiedFollowing"
    NEXT_BUSINESS_DAY = "NextBusinessDay"
    NO_MOVING = "NoMoving"
    PREVIOUS_BUSINESS_DAY = "PreviousBusinessDay"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(BusinessDayConvention, _CONVENTION_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_CONVENTION_VALUES_IN_LOWER_BY_CONVENTION, some)


_CONVENTION_VALUES = tuple(t.value for t in BusinessDayConvention)
_CONVENTION_VALUES_IN_LOWER_BY_CONVENTION = {
    name.lower(): item for name, item in BusinessDayConvention.__members__.items()
}
