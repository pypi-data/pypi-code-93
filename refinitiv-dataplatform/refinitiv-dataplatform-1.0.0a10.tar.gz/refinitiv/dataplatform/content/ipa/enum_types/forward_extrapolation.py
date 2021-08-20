# coding: utf8
# contract_gen 2020-05-18 08:30:59.239820

__all__ = ["ForwardExtrapolation"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class ForwardExtrapolation(Enum):
    CST_EXTRAPOL = "Cst_Extrapol"
    LINEAR_EXTRAPOL = "Linear_Extrapol"
    POWER_GROWTH_EXTRAPOL = "PowerGrowth_Extrapol"
    USE_DIVIDEND_EXTRAPOL = "UseDividendExtrapol"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            ForwardExtrapolation, _FORWARD_EXTRAPOLATION_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _FORWARD_EXTRAPOLATION_VALUES_IN_LOWER_BY_FORWARD_EXTRAPOLATION, some
        )


_FORWARD_EXTRAPOLATION_VALUES = tuple(t.value for t in ForwardExtrapolation)
_FORWARD_EXTRAPOLATION_VALUES_IN_LOWER_BY_FORWARD_EXTRAPOLATION = {
    name.lower(): item for name, item in ForwardExtrapolation.__members__.items()
}
