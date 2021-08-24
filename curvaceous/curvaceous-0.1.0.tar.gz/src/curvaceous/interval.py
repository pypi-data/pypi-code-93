from decimal import Decimal
from typing import TypeVar, Generic
from dataclasses import dataclass

import numpy as np


X = TypeVar("X", float, np.number, Decimal)


@dataclass(frozen=True)
class Interval(Generic[X]):
    lo: X
    hi: X

    def __contains__(self, x: X) -> bool:
        return self.lo <= x <= self.hi

    def __repr__(self) -> str:
        return "[{}, {}]".format(self.lo, self.hi)

    def closest(self, x: X) -> X:
        return min(self.hi, max(self.lo, x))  # type: ignore


def equidistant(interval: Interval, n: int) -> np.ndarray:
    """Create a grid of equidistant points.

    :param n: The number of points in the grid.
    """
    return np.linspace(interval.lo, interval.hi, n)
