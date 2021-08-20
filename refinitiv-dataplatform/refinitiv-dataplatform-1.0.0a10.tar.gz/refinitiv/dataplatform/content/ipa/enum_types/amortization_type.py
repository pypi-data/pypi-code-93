# coding: utf8
# contract_gen 2020-05-18 08:30:59.200816

__all__ = ["AmortizationType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class AmortizationType(Enum):
    ANNUITY = "Annuity"
    LINEAR = "Linear"
    NONE = "None"
    SCHEDULE = "Schedule"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(AmortizationType, _AMORTIZATION_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_AMORTIZATION_TYPE_VALUES_IN_LOWER_BY_AMORTIZATION_TYPE, some)


_AMORTIZATION_TYPE_VALUES = tuple(t.value for t in AmortizationType)
_AMORTIZATION_TYPE_VALUES_IN_LOWER_BY_AMORTIZATION_TYPE = {
    name.lower(): item for name, item in AmortizationType.__members__.items()
}
