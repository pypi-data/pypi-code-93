# coding: utf8
# contract_gen 2020-09-02 06:21:29.308976

__all__ = ["IndexConvexityAdjustmentIntegrationMethod"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class IndexConvexityAdjustmentIntegrationMethod(Enum):
    RIEMANN_SUM = "RiemannSum"
    RUNGE_KUTTA = "RungeKutta"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            IndexConvexityAdjustmentIntegrationMethod,
            _INDEX_CONVEXITY_ADJUSTMENT_INTEGRATION_METHOD_VALUES,
            some,
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _INDEX_CONVEXITY_ADJUSTMENT_INTEGRATION_METHOD_VALUES_IN_LOWER_BY_INDEX_CONVEXITY_ADJUSTMENT_INTEGRATION_METHOD,
            some,
        )


_INDEX_CONVEXITY_ADJUSTMENT_INTEGRATION_METHOD_VALUES = tuple(
    t.value for t in IndexConvexityAdjustmentIntegrationMethod
)
_INDEX_CONVEXITY_ADJUSTMENT_INTEGRATION_METHOD_VALUES_IN_LOWER_BY_INDEX_CONVEXITY_ADJUSTMENT_INTEGRATION_METHOD = {
    name.lower(): item
    for name, item in IndexConvexityAdjustmentIntegrationMethod.__members__.items()
}
