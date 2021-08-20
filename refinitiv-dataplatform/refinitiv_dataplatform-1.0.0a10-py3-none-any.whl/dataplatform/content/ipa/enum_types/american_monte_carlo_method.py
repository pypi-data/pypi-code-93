# coding: utf8
# contract_gen 2020-05-18 08:30:59.244816

__all__ = ["AmericanMonteCarloMethod"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class AmericanMonteCarloMethod(Enum):
    ANDERSEN = "Andersen"
    LONGSTAFF_SCHWARTZ = "LongstaffSchwartz"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            AmericanMonteCarloMethod, _AMERICAN_MONTE_CARLO_METHOD_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _AMERICAN_MONTE_CARLO_METHOD_VALUES_IN_LOWER_BY_AMERICAN_MONTE_CARLO_METHOD,
            some,
        )


_AMERICAN_MONTE_CARLO_METHOD_VALUES = tuple(t.value for t in AmericanMonteCarloMethod)
_AMERICAN_MONTE_CARLO_METHOD_VALUES_IN_LOWER_BY_AMERICAN_MONTE_CARLO_METHOD = {
    name.lower(): item for name, item in AmericanMonteCarloMethod.__members__.items()
}
