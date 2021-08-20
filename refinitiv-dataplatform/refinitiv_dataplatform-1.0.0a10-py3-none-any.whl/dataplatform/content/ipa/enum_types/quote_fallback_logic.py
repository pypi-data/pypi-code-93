# coding: utf8
# contract_gen 2020-09-02 06:21:29.297010

__all__ = ["QuoteFallbackLogic"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class QuoteFallbackLogic(Enum):
    BEST_FIELD = "BestField"
    NONE = "None"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(QuoteFallbackLogic, _QUOTE_FALLBACK_LOGIC_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(
            _QUOTE_FALLBACK_LOGIC_VALUES_IN_LOWER_BY_QUOTE_FALLBACK_LOGIC, some
        )


_QUOTE_FALLBACK_LOGIC_VALUES = tuple(t.value for t in QuoteFallbackLogic)
_QUOTE_FALLBACK_LOGIC_VALUES_IN_LOWER_BY_QUOTE_FALLBACK_LOGIC = {
    name.lower(): item for name, item in QuoteFallbackLogic.__members__.items()
}
