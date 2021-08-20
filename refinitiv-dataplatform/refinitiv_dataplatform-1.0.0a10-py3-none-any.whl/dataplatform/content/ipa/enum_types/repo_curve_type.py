# coding: utf8
# contract_gen 2020-05-18 08:30:59.233816

__all__ = ["RepoCurveType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class RepoCurveType(Enum):
    DEPOSIT_CURVE = "DepositCurve"
    LIBOR_FIXING = "LiborFixing"
    REPO_CURVE = "RepoCurve"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(RepoCurveType, _REPO_CURVE_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_REPO_CURVE_TYPE_VALUES_IN_LOWER_BY_REPO_CURVE_TYPE, some)


_REPO_CURVE_TYPE_VALUES = tuple(t.value for t in RepoCurveType)
_REPO_CURVE_TYPE_VALUES_IN_LOWER_BY_REPO_CURVE_TYPE = {
    name.lower(): item for name, item in RepoCurveType.__members__.items()
}
