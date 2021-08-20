# coding: utf8
# contract_gen 2020-05-18 08:30:59.217815

__all__ = ["FixingFrequency"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class FixingFrequency(Enum):
    DAILY = "Daily"
    BI_WEEKLY = "BiWeekly"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    QUATERLY = "Quaterly"
    SEMI_ANNUAL = "SemiAnnual"
    ANNUAL = "Annual"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(FixingFrequency, _FIXING_FREQUENCY_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_FIXING_FREQUENCY_VALUES_IN_LOWER_BY_FIXING_FREQUENCY, some)


_FIXING_FREQUENCY_VALUES = tuple(t.value for t in FixingFrequency)
_FIXING_FREQUENCY_VALUES_IN_LOWER_BY_FIXING_FREQUENCY = {
    name.lower(): item for name, item in FixingFrequency.__members__.items()
}
