# coding: utf8
# contract_gen 2020-05-18 08:30:59.218860

__all__ = ["InOrOut"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class InOrOut(Enum):
    IN = "In"
    OUT = "Out"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(InOrOut, _IN_OR_OUT_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_IN_OR_OUT_VALUES_IN_LOWER_BY_IN_OR_OUT, some)


_IN_OR_OUT_VALUES = tuple(t.value for t in InOrOut)
_IN_OR_OUT_VALUES_IN_LOWER_BY_IN_OR_OUT = {
    name.lower(): item for name, item in InOrOut.__members__.items()
}
