# coding: utf8
# contract_gen 2020-06-16 10:26:10.693191

__all__ = ["Format"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class Format(Enum):
    LIST = "List"
    MATRIX = "Matrix"
    N_DIMENSIONAL_ARRAY = "NDimensionalArray"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(Format, _FORMAT_VALUES, some)

    @staticmethod
    def normalize(some):
        return _normalize(_FORMAT_VALUES_IN_LOWER_BY_FORMAT, some)


_FORMAT_VALUES = tuple(t.value for t in Format)
_FORMAT_VALUES_IN_LOWER_BY_FORMAT = {
    name.lower(): item for name, item in Format.__members__.items()
}
