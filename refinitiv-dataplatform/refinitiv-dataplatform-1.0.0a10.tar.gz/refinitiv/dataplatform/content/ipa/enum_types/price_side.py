# coding: utf8
# contract_gen 2020-05-18 08:30:59.209815

__all__ = ["PriceSide"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class PriceSide(Enum):
    ASK = "Ask"
    BID = "Bid"
    LAST = "Last"
    MID = "Mid"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(PriceSide, _PRICE_SIDE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_PRICE_SIDE_VALUES_IN_LOWER_BY_PRICE_SIDE, some)


_PRICE_SIDE_VALUES = tuple(t.value for t in PriceSide)
_PRICE_SIDE_VALUES_IN_LOWER_BY_PRICE_SIDE = {
    name.lower(): item for name, item in PriceSide.__members__.items()
}
