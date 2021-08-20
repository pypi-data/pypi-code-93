# coding: utf8
# contract_gen 2020-09-02 06:21:29.309974

__all__ = ["IndexConvexityAdjustmentMethod"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class IndexConvexityAdjustmentMethod(Enum):
    NONE = "None"
    BLACK_SCHOLES = "BlackScholes"
    REPLICATION = "Replication"
    LINEAR_SWAP_MODEL = "LinearSwapModel"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            IndexConvexityAdjustmentMethod,
            _INDEX_CONVEXITY_ADJUSTMENT_METHOD_VALUES,
            some,
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _INDEX_CONVEXITY_ADJUSTMENT_METHOD_VALUES_IN_LOWER_BY_INDEX_CONVEXITY_ADJUSTMENT_METHOD,
            some,
        )


_INDEX_CONVEXITY_ADJUSTMENT_METHOD_VALUES = tuple(
    t.value for t in IndexConvexityAdjustmentMethod
)
_INDEX_CONVEXITY_ADJUSTMENT_METHOD_VALUES_IN_LOWER_BY_INDEX_CONVEXITY_ADJUSTMENT_METHOD = {
    name.lower(): item
    for name, item in IndexConvexityAdjustmentMethod.__members__.items()
}
