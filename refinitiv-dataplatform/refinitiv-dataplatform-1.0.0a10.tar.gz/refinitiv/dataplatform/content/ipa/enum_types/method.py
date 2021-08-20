# coding: utf8
# contract_gen 2020-05-18 08:30:59.244816

__all__ = ["Method"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class Method(Enum):
    AMERICAN_MONTE_CARLO = "AmericanMonteCarlo"
    ANALYTIC = "Analytic"
    MONTE_CARLO = "MonteCarlo"
    PDE = "PDE"
    TREE = "Tree"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(Method, _METHOD_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_METHOD_VALUES_IN_LOWER_BY_METHOD, some)


_METHOD_VALUES = tuple(t.value for t in Method)
_METHOD_VALUES_IN_LOWER_BY_METHOD = {
    name.lower(): item for name, item in Method.__members__.items()
}
