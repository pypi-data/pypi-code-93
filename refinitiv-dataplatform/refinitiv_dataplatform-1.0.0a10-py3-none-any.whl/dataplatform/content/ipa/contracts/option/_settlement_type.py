# coding: utf8

__all__ = ["SettlementType"]

from enum import Enum, unique
from refinitiv.dataplatform.content.ipa.enum_types.common_tools import (
    _convert_to_str,
    _normalize,
)


@unique
class SettlementType(Enum):
    UNDEFINED = "Undefined"
    CASH = "Cash"
    ASSET = "Asset"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(SettlementType, _SETTLEMENT_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_SETTLEMENT_TYPE_VALUES_IN_LOWER_BY_SETTLEMENT_TYPE, some)


_SETTLEMENT_TYPE_VALUES = (t.value for t in SettlementType)
_SETTLEMENT_TYPE_VALUES_IN_LOWER_BY_SETTLEMENT_TYPE = {
    name.lower(): item for name, item in SettlementType.__members__.items()
}
