# coding: utf8
# contract_gen 2020-05-18 08:30:59.197816

__all__ = ["DayCountBasis"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class DayCountBasis(Enum):
    DCB_30_E_360_ISMA = "Dcb_30E_360_ISMA"
    DCB_30_360 = "Dcb_30_360"
    DCB_30_360_GERMAN = "Dcb_30_360_German"
    DCB_30_360_ISDA = "Dcb_30_360_ISDA"
    DCB_30_360_US = "Dcb_30_360_US"
    DCB_30_365_BRAZIL = "Dcb_30_365_Brazil"
    DCB_30_365_GERMAN = "Dcb_30_365_German"
    DCB_30_365_ISDA = "Dcb_30_365_ISDA"
    DCB_30_ACTUAL = "Dcb_30_Actual"
    DCB_30_ACTUAL_GERMAN = "Dcb_30_Actual_German"
    DCB_30_ACTUAL_ISDA = "Dcb_30_Actual_ISDA"
    DCB_ACTUAL_LEAP_DAY_360 = "Dcb_ActualLeapDay_360"
    DCB_ACTUAL_LEAP_DAY_365 = "Dcb_ActualLeapDay_365"
    DCB_ACTUAL_360 = "Dcb_Actual_360"
    DCB_ACTUAL_364 = "Dcb_Actual_364"
    DCB_ACTUAL_365 = "Dcb_Actual_365"
    DCB_ACTUAL_36525 = "Dcb_Actual_36525"
    DCB_ACTUAL_365_L = "Dcb_Actual_365L"
    DCB_ACTUAL_365_P = "Dcb_Actual_365P"
    DCB_ACTUAL_365_CANADIAN_CONVENTION = "Dcb_Actual_365_CanadianConvention"
    DCB_ACTUAL_ACTUAL = "Dcb_Actual_Actual"
    DCB_ACTUAL_ACTUAL_AFB = "Dcb_Actual_Actual_AFB"
    DCB_ACTUAL_ACTUAL_ISDA = "Dcb_Actual_Actual_ISDA"
    DCB_CONSTANT = "Dcb_Constant"
    DCB_WORKING_DAYS_252 = "Dcb_WorkingDays_252"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(DayCountBasis, _DAY_COUNT_BASIS_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_DAY_COUNT_BASIS_VALUES_IN_LOWER_BY_DAY_COUNT_BASIS, some)


_DAY_COUNT_BASIS_VALUES = tuple(t.value for t in DayCountBasis)
_DAY_COUNT_BASIS_VALUES_IN_LOWER_BY_DAY_COUNT_BASIS = {
    name.lower(): item for name, item in DayCountBasis.__members__.items()
}
