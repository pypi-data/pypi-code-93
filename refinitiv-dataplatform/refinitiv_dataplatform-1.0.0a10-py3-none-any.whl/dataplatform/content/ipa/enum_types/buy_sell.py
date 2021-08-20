# coding: utf8
# contract_gen 2020-05-18 08:30:59.216815

__all__ = ["BuySell"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class BuySell(Enum):
    BUY = "Buy"
    SELL = "Sell"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(BuySell, _BUY_SELL_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_BUY_SELL_VALUES_IN_LOWER_BY_BUY_SELL, some)


_BUY_SELL_VALUES = tuple(t.value for t in BuySell)
_BUY_SELL_VALUES_IN_LOWER_BY_BUY_SELL = {
    name.lower(): item for name, item in BuySell.__members__.items()
}
