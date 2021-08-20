# coding: utf8
# contract_gen 2020-05-18 08:30:59.238824

__all__ = ["ForwardComputeMethod"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class ForwardComputeMethod(Enum):
    USE_DIVIDENDS_ONLY = "UseDividendsOnly"
    USE_FORWARD_CRV = "UseForwardCrv"
    USE_FORWARD_CRV_AND_DIVIDENDS = "UseForwardCrvAndDividends"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            ForwardComputeMethod, _FORWARD_COMPUTE_METHOD_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _FORWARD_COMPUTE_METHOD_VALUES_IN_LOWER_BY_FORWARD_COMPUTE_METHOD, some
        )


_FORWARD_COMPUTE_METHOD_VALUES = tuple(t.value for t in ForwardComputeMethod)
_FORWARD_COMPUTE_METHOD_VALUES_IN_LOWER_BY_FORWARD_COMPUTE_METHOD = {
    name.lower(): item for name, item in ForwardComputeMethod.__members__.items()
}
