# coding: utf8
# contract_gen 2020-05-18 08:30:59.246815

__all__ = ["NotionalExchange"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class NotionalExchange(Enum):
    BOTH = "Both"
    END = "End"
    END_ADJUSTMENT = "EndAdjustment"
    NONE = "None"
    START = "Start"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(NotionalExchange, _NOTIONAL_EXCHANGE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_NOTIONAL_EXCHANGE_VALUES_IN_LOWER_BY_NOTIONAL_EXCHANGE, some)


_NOTIONAL_EXCHANGE_VALUES = tuple(t.value for t in NotionalExchange)
_NOTIONAL_EXCHANGE_VALUES_IN_LOWER_BY_NOTIONAL_EXCHANGE = {
    name.lower(): item for name, item in NotionalExchange.__members__.items()
}
