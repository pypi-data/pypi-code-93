# coding: utf8
# contract_gen 2020-05-18 08:30:59.208846

__all__ = ["BenchmarkYieldSelectionMode"]

from enum import Enum, unique
from .common_tools import _convert_to_str, _normalize


@unique
class BenchmarkYieldSelectionMode(Enum):
    INTERPOLATE = "Interpolate"
    NEAREST = "Nearest"

    @staticmethod
    def convert_to_str(some):
        return _convert_to_str(
            BenchmarkYieldSelectionMode, _BENCHMARK_YIELD_SELECTION_MODE_VALUES, some
        )

    @staticmethod
    def normalize(some):
        return _normalize(
            _BENCHMARK_YIELD_SELECTION_MODE_VALUES_IN_LOWER_BY_BENCHMARK_YIELD_SELECTION_MODE,
            some,
        )


_BENCHMARK_YIELD_SELECTION_MODE_VALUES = tuple(
    t.value for t in BenchmarkYieldSelectionMode
)
_BENCHMARK_YIELD_SELECTION_MODE_VALUES_IN_LOWER_BY_BENCHMARK_YIELD_SELECTION_MODE = {
    name.lower(): item for name, item in BenchmarkYieldSelectionMode.__members__.items()
}
