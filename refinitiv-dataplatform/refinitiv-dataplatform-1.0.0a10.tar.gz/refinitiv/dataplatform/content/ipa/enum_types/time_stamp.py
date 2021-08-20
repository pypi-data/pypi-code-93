# coding: utf8
# contract_gen 2020-05-18 08:30:59.230815

__all__ = ["TimeStamp"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class TimeStamp(Enum):
    DEFAULT = "Default"
    OPEN = "Open"
    CLOSE = "Close"
    SETTLE = "Settle"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(TimeStamp, _TIME_STAMP_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_TIME_STAMP_VALUES_IN_LOWER_BY_TIME_STAMP, some)


_TIME_STAMP_VALUES = tuple(t.value for t in TimeStamp)
_TIME_STAMP_VALUES_IN_LOWER_BY_TIME_STAMP = {
    name.lower(): item for name, item in TimeStamp.__members__.items()
}
