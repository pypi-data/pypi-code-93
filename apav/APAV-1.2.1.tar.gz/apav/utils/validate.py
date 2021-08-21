"""
This file is part of APAV.

APAV is a python package for performing analysis and visualization on
atom probe tomography data sets.

Copyright (C) 2018 Jesse Smith

APAV is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

APAV is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with APAV.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import annotations

import os
import numpy as n

import apav.utils.helpers as helpers
from apav.utils.hinting import *


int_types = (int, n.int64, n.int32, n.int16, n.int8)


class NoMultiEventError(Exception):
    """
    Raise when an operation requires multiple hit information (i.e. originates from an epos file) but
    that information is not available
    """
    def __init__(self):
        super().__init__("Roi has no multiple-event information")


class NoDetectorInfoError(Exception):
    """
    Raise when an operation requires detector specific information (i.e. originates from an epos file) but
    that information is not available
    """
    def __init__(self):
        super().__init__("Roi has no detector coordinate information")


class NoTOFError(Exception):
    """
    Raise when an operation requires time-of-flight information (i.e. originates from an epos file) but
    that information is not available
    """
    def __init__(self):
        super().__init__("Roi has no time-of-flight information")


class AbstractMethodError(Exception):
    """
    Raise when a call to an abstract method
    """
    def __init__(self):
        super().__init__("Call to abstract method is not allowed")


class IntervalIntersectionError(Exception):
    """
    Raise when two intervals intersect, but shouldn't
    """
    def __init__(self, msg: str = None):
        if msg is None:
            msg = f"Intersection between intervals is not allowed"
        super().__init__(msg)


class IonTypeError(Exception):
    """
    Raise when an :class:`Ion` was expected but not provided
    """
    def __init__(self, other):
        super().__init__(f"Expected an Ion type not {type(other)}")


def boolean(val) -> bool:
    """
    Validate a boolean value, only bool allowed not 0 or 1

    :param val: the boolean value to validate
    """
    if val not in (True, False):
        raise TypeError(f"{val} is not a boolean value")
    else:
        return val


def is_type(val, kind):
    if isinstance(val, kind):
        return val
    else:
        raise TypeError("Expected type {} not {}".format(kind, type(val)))


def file_exists(fpath: str) -> str:
    """
    Validate that a file exists

    :param fpath: the file path to validate existence
    """
    if not os.path.exists(fpath):
        raise FileNotFoundError(f"The path {fpath} does not exist")
    elif not os.path.isfile(fpath):
        raise IOError(f"The path {fpath} is not a file")

    return fpath


def color_as_rgb(val) -> Tuple[Real, Real, Real]:
    """
    Validate that an input is a normalized color RGB value, convert if possible

    :param val: the color to validate
    """
    if isinstance(val, (tuple, list)):
        if not len(val) == 3 or not all(0 <= i <= 1 for i in val) or any(i < 0 for i in val):
            raise ValueError("Invalid color")
        return val
    elif isinstance(val, str):
        if len(val) != 6:
            raise ValueError("Hex string colors must be 6 characters long")
        rgb = helpers.hex2rgbF(val)
        return rgb
    else:
        raise TypeError("Invalid color type")


def interval(val: tuple):
    """
    Validate a numeric interval

    :param val: the interval to validate
    """
    if not isinstance(val, (tuple, list)):
        raise TypeError("Invalid interval type")
    elif len(val) != 2:
        raise ValueError("Invalid interval input")
    elif (val[1] <= val[0]):
        raise ValueError(f"Invalid interval ({val[0]} - {val[1]}), expected a sequential interval")

    return tuple(val)


def positive_interval(val: tuple) -> tuple:
    """
    Validate that an input is a positive range sequence

    :param val: the interval to validate
    """
    if not isinstance(val, (tuple, list)):
        raise TypeError("Invalid interval type")
    elif len(val) != 2:
        raise ValueError("Invalid interval input")
    elif (val[1] <= val[0]) or any(i < 0 for i in val):
        raise ValueError(f"Invalid interval extents ({val[0]} - {val[1]}), expected positive interval")

    return tuple(val)


def positive_interval_2d(val: (tuple, tuple)) -> (tuple, tuple):
    """
    Validate that an input is a positive range sequence in two dimensions

    :param val: the interval to validate
    """
    if not isinstance(val, (tuple, list)):
        raise TypeError("Invalid range type")

    pair1, pair2 = val

    if len(val) != 2:
        raise ValueError("Invalid interval input")
    if (pair1[1] <= pair1[0]) or any(i < 0 for i in pair1):
        raise ValueError(f"Invalid interval extents")
    if (pair2[1] <= pair2[0]) or any(i < 0 for i in pair2):
        raise ValueError(f"Invalid interval extents")

    return tuple(val)


def positive_number(val):
    """
    Validate that an input is a positive number

    :param val: the number to validate
    """
    if not isinstance(val, (int, float)):
        raise TypeError("Invalid type for number")
    elif not val >= 0:
        raise ValueError(f"Expected value >= 0, instead got {val} instead")

    return val


def positive_nonzero_number(val):
    """
    Validate that an input is a positive number

    :param val: the number to validate
    """
    if not isinstance(val, (int, float)):
        raise TypeError("Invalid type for number")
    elif not val > 0:
        raise ValueError(f"Expected value > 0 instead got {val} instead")

    return val


def positive_nonzero_int(val):
    """
    Validate that an input is a positive number

    :param val: the number to validate
    """
    if val % 1 != 0:
        raise TypeError("Integral value required")
    elif not val > 0:
        raise ValueError(f"Expected value > 0 instead got {val} instead")

    return val


def number_in_interval(val, lower, upper, lower_open=True, upper_open=True):
    """
    Validate that a number is contained within an interval.

    :param val: the number to validate
    :param lower: the lower bound of the interval
    :param upper: the upper bound of the interval
    :param lower_open: whether or not the lower bound is open
    :param upper_open: whether or not the upper bound is open
    """
    valid = True
    if val < lower or val > upper:
        valid = False

    if lower_open is True:
        if val == lower:
            valid = False
    if upper_open is True:
        if val == upper:
            valid = False

    left = "(" if lower_open else "["
    right = ")" if upper_open else "]"

    if not valid:
        raise ValueError(f"The value {val} is not in the interval {left}{lower}, {upper}{right} ")
    else:
        return val


def multiplicity_any(val):
    """
    Any integral multiplicity value >= 1 or 'all' or 'multiples'

    :param val: the multiplicity to validate
    """
    msg = "Expected a multiplicity of int >= 1 or `all` or 'multiples'"
    if isinstance(val, str):
        if val not in ("all", "multiples"):
            raise ValueError(msg)
    elif isinstance(val, int_types):
        if not val >= 1:
            raise ValueError(msg)
    elif not isinstance(val, (str, int)):
        raise TypeError(msg)
    return val


def multiplicity_any_singular_or_all_multiples(val):
    """
    Any integral multiplicity value >= 1 or 'multiples'

    :param val: the multiplicity to validate
    """
    msg = "Expected a multiplicity of int >= 1 or 'multiples'"
    if isinstance(val, str):
        if val != "multiples":
            raise ValueError(msg)
    elif isinstance(val, int_types):
        if not val >= 1:
            raise ValueError(msg)
    elif not isinstance(val, (str, int)):
        raise TypeError(msg)
    return val


def multiplicity_singular_two_or_greater(val) -> int:
    """
    Any integral multiplicity value >= 2

    :param val: the multiplicity to validate
    """
    msg = "Expected a multiplicity value of int >= 2"
    if not isinstance(val, int_types):
        raise TypeError(msg)
    elif not val >= 2:
        raise ValueError(msg)
    else:
        return int(val)


def multiplicity_singular_one_or_greater(val) -> int:
    """
    Any integral multiplicity value >= 1

    :param val: the multiplicity to validate
    """
    msg = "Expected a multiplicity value of int >= 1"
    if not isinstance(val, int_types):
        raise TypeError(msg)
    elif not val >= 1:
        raise ValueError(msg)
    else:
        return int(val)


def multiplicity_non_singles(val) -> Union[int, str]:
    """
    Validate that a given multiplicity value is any int > 1 or "multiples"

    :param val: the multiplicity to validate
    """
    msg = f"Expected a multiplicity value of int >= 2 or \"multiples\", got {val} of type {type(val)} instead"
    if isinstance(val, int_types):
        if not val >= 2:
            raise ValueError(msg)
        else:
            return int(val)
    elif isinstance(val, str):
        if val != "multiples":
            raise ValueError(msg)
        else:
            return val
    else:
        raise ValueError(msg)


def choice(val: Any, possible_vals: Sequence[Any]):
    """
    Validate that a value is one of a set of possible values

    :param val: the option to validate
    :param possible_vals: the list of possible options
    """
    if val not in possible_vals:
        raise ValueError(f"'{val}' is not one of {possible_vals}")
    return val


def all_positive_nonzero(seq: Sequence[Real]):
    """
    Validate that all numbers of a sequence are positive and non-zero

    :param seq: the sequence to validate
    """
    if any(i <= 0 for i in seq):
        raise ValueError("Expected a sequence of all positive non-zero values")
    return seq

