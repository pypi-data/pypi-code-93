# coding: utf8
# contract_gen 2020-05-18 08:30:59.231843

__all__ = ["PricingModelType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class PricingModelType(Enum):
    BINOMIAL = "Binomial"
    BLACK_SCHOLES = "BlackScholes"
    CEV = "CEV"
    CONTINUOUS = "Continuous"
    LOCAL_VOLATILITY = "LocalVolatility"
    TRINOMIAL = "Trinomial"
    VANNA_VOLGA = "VannaVolga"
    WHALEY = "Whaley"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(PricingModelType, _PRICING_MODEL_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(
            _PRICING_MODEL_TYPE_VALUES_IN_LOWER_BY_PRICING_MODEL_TYPE, some
        )


_PRICING_MODEL_TYPE_VALUES = tuple(t.value for t in PricingModelType)
_PRICING_MODEL_TYPE_VALUES_IN_LOWER_BY_PRICING_MODEL_TYPE = {
    name.lower(): item for name, item in PricingModelType.__members__.items()
}
