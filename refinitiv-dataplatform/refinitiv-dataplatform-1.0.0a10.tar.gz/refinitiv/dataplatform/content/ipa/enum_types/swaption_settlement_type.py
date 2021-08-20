# coding: utf8
# contract_gen 2020-05-18 08:30:59.248815

__all__ = ["SwaptionSettlementType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class SwaptionSettlementType(Enum):
    CASH = "Cash"
    PHYSICAL = "Physical"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            SwaptionSettlementType, _SWAPTION_SETTLEMENT_TYPE_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _SWAPTION_SETTLEMENT_TYPE_VALUES_IN_LOWER_BY_SWAPTION_SETTLEMENT_TYPE, some
        )


_SWAPTION_SETTLEMENT_TYPE_VALUES = tuple(t.value for t in SwaptionSettlementType)
_SWAPTION_SETTLEMENT_TYPE_VALUES_IN_LOWER_BY_SWAPTION_SETTLEMENT_TYPE = {
    name.lower(): item for name, item in SwaptionSettlementType.__members__.items()
}
