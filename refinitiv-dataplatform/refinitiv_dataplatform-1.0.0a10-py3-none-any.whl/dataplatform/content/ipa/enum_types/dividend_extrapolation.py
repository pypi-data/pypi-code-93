# coding: utf8
# contract_gen 2020-05-18 08:30:59.235841

__all__ = ["DividendExtrapolation"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class DividendExtrapolation(Enum):
    CST_EXTRAPOL = "Cst_Extrapol"
    LINEAR_EXTRAPOL = "Linear_Extrapol"
    POWER_GROWTH_EXTRAPOL = "PowerGrowth_Extrapol"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            DividendExtrapolation, _DIVIDEND_EXTRAPOLATION_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _DIVIDEND_EXTRAPOLATION_VALUES_IN_LOWER_BY_DIVIDEND_EXTRAPOLATION, some
        )


_DIVIDEND_EXTRAPOLATION_VALUES = tuple(t.value for t in DividendExtrapolation)
_DIVIDEND_EXTRAPOLATION_VALUES_IN_LOWER_BY_DIVIDEND_EXTRAPOLATION = {
    name.lower(): item for name, item in DividendExtrapolation.__members__.items()
}
