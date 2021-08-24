from typing import TextIO, Optional
from numbers import Number

import numpy as np
from numpy.typing import ArrayLike

import pandas as pd
from curvaceous.interval import Interval


class Curve:
    xs: np.ndarray
    ys: np.ndarray

    def __init__(self, xs: ArrayLike, ys: ArrayLike):
        if not isinstance(xs, np.ndarray):
            xs = np.array(xs)
        if not isinstance(ys, np.ndarray):
            ys = np.array(ys)
        if len(xs) != len(ys):
            raise ValueError("Coordinate lists need to be of equal length")
        self.xs = xs
        self.ys = ys

    def __len__(self):
        return len(self.xs)

    @classmethod
    def read(cls, h: TextIO):
        df = pd.read_csv(h)
        # pylint: disable=no-member
        return cls(df.platform_costs.values, df.platform_clicks.values)

    @classmethod
    def from_dict(cls, m):
        return cls(m["xs"], m["ys"])

    @property
    def domain(self):
        return Interval(np.min(self.xs), np.max(self.xs))

    def __call__(self, c, *, cut=False) -> Optional[Number]:
        if cut:
            c = self.domain.closest(c)
        if c not in self.domain:
            return None
        i = np.argmax(self.xs > c)
        if i == 0:  # c == self.domain.hi
            return self.ys[-1]
        width = self.xs[i] - self.xs[i - 1]
        u = (c - self.xs[i - 1]) / width
        v = (self.xs[i] - c) / width
        return v * self.ys[i - 1] + u * self.ys[i]

    def __add__(self, other):
        if isinstance(other, Curve):
            xs = np.unique(np.concatenate((self.xs, other.xs)))
            ys = np.array([self(x) + other(x) for x in xs])
            return Curve(xs, ys)
        if isinstance(other, (int, float)):
            return Curve(self.xs, self.ys + other)
        raise ValueError()

    def __sub__(self, other):
        if isinstance(other, Curve):
            xs = np.unique(np.concatenate((self.xs, other.xs)))
            ys = np.array([self(x) - other(x) for x in xs])
            return Curve(xs, ys)
        if isinstance(other, (int, float)):
            return Curve(self.xs, self.ys - other)
        raise ValueError()

    def __eq__(self, other):
        # IMPROVE: This test equality of representation, not of semantics
        if not isinstance(other, Curve):
            return False
        return (other.xs == self.xs).all() and (other.ys == self.ys).all()

    def resample(self, cs):
        xs = []
        ys = []
        for x in cs:
            if x in self.domain:
                xs.append(x)
                ys.append(self(x))
        return Curve(xs, ys)

    def derivative(self):
        hs = self.ys[1:] - self.ys[:-1]
        ws = self.xs[1:] - self.xs[:-1]
        return Curve(self.xs[:-1], hs / ws)

    def grow(self, factor):
        return Curve(factor * self.xs, factor * self.ys)

    def to_dict(self):
        return {"xs": list(self.xs), "ys": list(self.ys)}

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self.domain, len(self.xs))


def max_with_constant(threshold, curve: Curve):
    """Compute the maximum of the curve with some constant

    :param threshold: The constant
    :param curve: The piecewise linear curve
    :returns: Another piecewise linear curve
    """
    xs = [curve.xs[0]]
    ys = [max(curve.ys[0], threshold)]
    above_threshold = curve.ys[0] > threshold
    for i in range(1, len(curve)):
        if curve.ys[i] > threshold and above_threshold:
            xs.append(curve.xs[i])
            ys.append(curve.ys[i])
        elif curve.ys[i] > threshold and not above_threshold:
            above_threshold = True
            xs.append(
                _intersect(
                    threshold, curve.xs[i - 1], curve.xs[i], curve.ys[i - 1], curve.ys[i]
                )
            )
            xs.append(curve.xs[i])
            ys.append(threshold)
            ys.append(curve.ys[i])
        elif curve.ys[i] <= threshold and above_threshold:
            above_threshold = False
            xs.append(
                _intersect(
                    threshold, curve.xs[i - 1], curve.xs[i], curve.ys[i - 1], curve.ys[i]
                )
            )
            ys.append(threshold)

        elif curve.ys[i] <= threshold and not above_threshold:
            pass
    if not above_threshold:
        xs.append(curve.xs[-1])
        ys.append(threshold)
    return Curve(xs, ys)


def _intersect(threshold, x_min, x_max, y_min, y_max):
    p = threshold - y_min / (y_max - y_min)
    return x_min + p * (x_max - x_min)


def distance(curve1: Curve, curve2: Curve):
    """The maximum pointwise distance between curves."""
    xs = np.unique(np.concatenate((curve1.xs, curve2.xs)))
    y_ = np.abs(curve1(xs[0]) - curve2(xs[0]))  # type: ignore
    x_ = xs[0]
    for x in xs[1:]:
        y = np.abs(curve1(x) - curve2(x))  # type: ignore
        if y > y_:
            x_ = x
            y_ = y
    return (x_, y_)
