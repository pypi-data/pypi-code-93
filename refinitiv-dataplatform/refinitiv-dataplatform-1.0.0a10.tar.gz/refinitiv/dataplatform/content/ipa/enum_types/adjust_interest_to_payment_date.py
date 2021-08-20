# coding: utf8
# contract_gen 2020-05-18 08:30:59.199816

__all__ = ["AdjustInterestToPaymentDate"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class AdjustInterestToPaymentDate(Enum):
    ADJUSTED = "Adjusted"
    UNADJUSTED = "Unadjusted"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            AdjustInterestToPaymentDate, _ADJUST_INTEREST_TO_PAYMENT_DATE_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _ADJUST_INTEREST_TO_PAYMENT_DATE_VALUES_IN_LOWER_BY_ADJUST_INTEREST_TO_PAYMENT_DATE,
            some,
        )


_ADJUST_INTEREST_TO_PAYMENT_DATE_VALUES = tuple(
    t.value for t in AdjustInterestToPaymentDate
)
_ADJUST_INTEREST_TO_PAYMENT_DATE_VALUES_IN_LOWER_BY_ADJUST_INTEREST_TO_PAYMENT_DATE = {
    name.lower(): item for name, item in AdjustInterestToPaymentDate.__members__.items()
}
