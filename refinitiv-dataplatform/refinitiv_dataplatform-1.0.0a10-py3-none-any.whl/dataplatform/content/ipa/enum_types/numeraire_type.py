# coding: utf8
# contract_gen 2020-05-18 08:30:59.243815

__all__ = ["NumeraireType"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class NumeraireType(Enum):
    CASH = "Cash"
    ROLLING_EVENT = "RollingEvent"
    ROLLING_PAYMENT = "RollingPayment"
    TERMINAL_EVENT_ZC = "TerminalEventZc"
    TERMINAL_ZC = "TerminalZc"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(NumeraireType, _NUMERAIRE_TYPE_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_NUMERAIRE_TYPE_VALUES_IN_LOWER_BY_NUMERAIRE_TYPE, some)


_NUMERAIRE_TYPE_VALUES = tuple(t.value for t in NumeraireType)
_NUMERAIRE_TYPE_VALUES_IN_LOWER_BY_NUMERAIRE_TYPE = {
    name.lower(): item for name, item in NumeraireType.__members__.items()
}
