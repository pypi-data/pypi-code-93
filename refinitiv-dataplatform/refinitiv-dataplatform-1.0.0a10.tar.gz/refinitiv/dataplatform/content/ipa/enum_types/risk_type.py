# coding: utf8
# contract_gen 2020-06-15 10:07:47.551305

__all__ = ["RiskType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class RiskType(Enum):
    INTEREST_RATE = "InterestRate"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(RiskType, _RISK_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_RISK_TYPE_VALUES_IN_LOWER_BY_RISK_TYPE, some)


_RISK_TYPE_VALUES = tuple(t.value for t in RiskType)
_RISK_TYPE_VALUES_IN_LOWER_BY_RISK_TYPE = {
    name.lower(): item for name, item in RiskType.__members__.items()
}
