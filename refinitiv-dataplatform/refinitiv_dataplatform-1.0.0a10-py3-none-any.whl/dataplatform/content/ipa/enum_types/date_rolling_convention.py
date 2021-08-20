# coding: utf8
# contract_gen 2020-05-18 08:30:59.206816

__all__ = ["DateRollingConvention"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class DateRollingConvention(Enum):
    LAST = "Last"
    LAST28 = "Last28"
    SAME = "Same"
    SAME28 = "Same28"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            DateRollingConvention, _PAYMENT_ROLL_CONVENTION_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _PAYMENT_ROLL_CONVENTION_VALUES_IN_LOWER_BY_PAYMENT_ROLL_CONVENTION, some
        )


_PAYMENT_ROLL_CONVENTION_VALUES = tuple(t.value for t in DateRollingConvention)
_PAYMENT_ROLL_CONVENTION_VALUES_IN_LOWER_BY_PAYMENT_ROLL_CONVENTION = {
    name.lower(): item for name, item in DateRollingConvention.__members__.items()
}
