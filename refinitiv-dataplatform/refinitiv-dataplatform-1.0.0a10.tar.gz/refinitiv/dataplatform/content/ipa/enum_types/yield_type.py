# coding: utf8
# contract_gen 2020-05-18 08:30:59.213816

__all__ = ["YieldType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class YieldType(Enum):
    ANNUAL_EQUIVALENT = "Annual_Equivalent"
    BOND_ACTUAL_364 = "Bond_Actual_364"
    BRAESS_FANGMEYER = "Braess_Fangmeyer"
    DISCOUNT_ACTUAL_360 = "Discount_Actual_360"
    DISCOUNT_ACTUAL_365 = "Discount_Actual_365"
    EUROLAND = "Euroland"
    ISMA = "Isma"
    JAPANESE_COMPOUNDED = "Japanese_Compounded"
    JAPANESE_SIMPLE = "Japanese_Simple"
    MONEY_MARKET_ACTUAL_360 = "MoneyMarket_Actual_360"
    MONEY_MARKET_ACTUAL_365 = "MoneyMarket_Actual_365"
    MONEY_MARKET_ACTUAL_ACTUAL = "MoneyMarket_Actual_Actual"
    MOOSMUELLER = "Moosmueller"
    NATIVE = "Native"
    QUARTERLY_EQUIVALENT = "Quarterly_Equivalent"
    SEMIANNUAL_EQUIVALENT = "Semiannual_Equivalent"
    TURKISH_COMPOUNDED = "TurkishCompounded"
    US_GOVT = "UsGovt"
    US_T_BILLS = "UsTBills"
    WEEKEND = "Weekend"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(YieldType, _YIELD_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_YIELD_TYPE_VALUES_IN_LOWER_BY_YIELD_TYPE, some)


_YIELD_TYPE_VALUES = tuple(t.value for t in YieldType)
_YIELD_TYPE_VALUES_IN_LOWER_BY_YIELD_TYPE = {
    name.lower(): item for name, item in YieldType.__members__.items()
}
