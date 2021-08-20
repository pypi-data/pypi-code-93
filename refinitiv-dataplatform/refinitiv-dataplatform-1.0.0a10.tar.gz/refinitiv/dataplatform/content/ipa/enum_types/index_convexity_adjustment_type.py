# coding: utf8
# contract_gen 2020-05-18 08:30:59.247816

__all__ = ["IndexConvexityAdjustmentType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class IndexConvexityAdjustmentType(Enum):
    NONE = "None"
    BLACK_SCHOLES = "BlackScholes"
    REPLICATION = "Replication"
    LIBOR_SWAP_METHOD = "LiborSwapMethod"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            IndexConvexityAdjustmentType, _INDEX_CONVEXITY_ADJUSTMENT_TYPE_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _INDEX_CONVEXITY_ADJUSTMENT_TYPE_VALUES_IN_LOWER_BY_INDEX_CONVEXITY_ADJUSTMENT_TYPE,
            some,
        )


_INDEX_CONVEXITY_ADJUSTMENT_TYPE_VALUES = tuple(
    t.value for t in IndexConvexityAdjustmentType
)
_INDEX_CONVEXITY_ADJUSTMENT_TYPE_VALUES_IN_LOWER_BY_INDEX_CONVEXITY_ADJUSTMENT_TYPE = {
    name.lower(): item
    for name, item in IndexConvexityAdjustmentType.__members__.items()
}
