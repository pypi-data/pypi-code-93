# coding: utf8
# contract_gen 2020-06-16 10:26:10.696189

__all__ = ["Axis"]

from enum import Enum, unique

from .common_tools import _convert_to_str, _normalize


@unique
class Axis(Enum):
    X = "X"
    Y = "Y"
    Z = "Z"
    DATE = "Date"
    DELTA = "Delta"
    EXPIRY = "Expiry"
    MONEYNESS = "Moneyness"
    STRIKE = "Strike"
    TENOR = "Tenor"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(Axis, _AXIS_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_AXIS_VALUES_IN_LOWER_BY_AXIS, some)


_AXIS_VALUES = tuple(t.value for t in Axis)
_AXIS_VALUES_IN_LOWER_BY_AXIS = {
    name.lower(): item for name, item in Axis.__members__.items()
}
