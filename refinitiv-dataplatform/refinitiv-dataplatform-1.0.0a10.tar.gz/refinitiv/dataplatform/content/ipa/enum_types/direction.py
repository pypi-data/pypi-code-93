# coding: utf8
# contract_gen 2020-05-18 08:30:59.201816

__all__ = ["Direction"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class Direction(Enum):
    PAID = "Paid"
    RECEIVED = "Received"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(Direction, _DIRECTION_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_DIRECTION_VALUES_IN_LOWER_BY_DIRECTION, some)


_DIRECTION_VALUES = tuple(t.value for t in Direction)
_DIRECTION_VALUES_IN_LOWER_BY_DIRECTION = {
    name.lower(): item for name, item in Direction.__members__.items()
}
