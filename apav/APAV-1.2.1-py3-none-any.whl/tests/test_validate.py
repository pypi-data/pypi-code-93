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
import os
from apav.utils.hinting import *

from pytest import raises

from apav.utils import validate


def test_boolean():
    validate.boolean(False)
    validate.boolean(True)
    with raises(TypeError):
        validate.boolean(0)
        validate.boolean(1)
        validate.boolean("False")


def test_is_type():
    assert validate.is_type(5.0, float) == 5.0

    validate.is_type(5, Real)
    validate.is_type(5.0, Real)

    with raises(TypeError):
        validate.is_type(5, float)
    with raises(TypeError):
        validate.is_type(5.0, int)


def test_file_exists():
    with open(".test_file", "w") as f:
        f.write("test")

        validate.file_exists(".test_file")
    os.remove(".test_file")

    with raises(Exception):
        validate.file_exists(".test_file")

    dirpath = ".__fake_path_directory_1234"
    os.makedirs(dirpath)
    with raises(Exception):
        validate.file_exists(dirpath)
    os.removedirs(dirpath)


def test_color_rgb():
    with raises(TypeError):
        validate.color_as_rgb(2)
    with raises(ValueError):
        validate.color_as_rgb((2, 0, 0))
    with raises(Exception):
        validate.color_as_rgb("1234")

    validate.color_as_rgb((0, 0.1, 0.5))
    validate.color_as_rgb("FFFFFF")
    assert (0, 0, 0) == validate.color_as_rgb("000000")


def test_interval():
    validate.interval((1, 2))
    validate.interval([1, 2])
    validate.interval((-32, 2))
    validate.interval((0, 2))
    validate.interval((-21, -10))

    with raises(ValueError):
        validate.interval((2, 1))
    with raises(ValueError):
        validate.interval((-2, -5))
    with raises(ValueError):
        validate.interval((1, 1))
    with raises(TypeError):
        validate.interval("1")
    with raises(ValueError):
        validate.interval((1, 2, 3))


def test_positive_interval():
    validate.positive_interval((0, 5))
    with raises(ValueError):
        validate.positive_interval((-1, 5))
    with raises(ValueError):
        validate.positive_interval((5, 1))
    with raises(ValueError):
        validate.positive_interval((2, 2))
    with raises(ValueError):
        validate.positive_interval((-2, -1))
    with raises(ValueError):
        validate.positive_interval((1, 2, 3))

    with raises(TypeError):
        validate.positive_interval("asdf")


def test_positive_interval2d():
    validate.positive_interval_2d(((0, 5), (1, 2)))
    validate.positive_interval_2d([[0, 5], [1, 2]])
    with raises(TypeError):
        validate.positive_interval_2d("asdf")

    with raises(ValueError):
        validate.positive_interval_2d(((5, 5), (12, 14)))
    with raises(ValueError):
        validate.positive_interval_2d(((-1, 6), (2, 3)))
    with raises(ValueError):
        validate.positive_interval_2d(((1, 6), (0, 0)))
    with raises(ValueError):
        validate.positive_interval_2d(((0, 0), (2, 3)))


def test_positive_number():
    validate.positive_number(0)
    validate.positive_number(4)
    with raises(ValueError):
        validate.positive_number(-1)


def test_positive_nonzero_number():
    validate.positive_nonzero_number(1)
    with raises(Exception):
        validate.positive_nonzero_number(-1)
    with raises(Exception):
        validate.positive_nonzero_number(0)


def test_positive_nonzero_int():
    validate.positive_nonzero_int(1)
    validate.positive_nonzero_int(2)
    with raises(ValueError):
        validate.positive_nonzero_int(0)
    with raises(ValueError):
        validate.positive_nonzero_int(-2)
    with raises(TypeError):
        validate.positive_nonzero_int("1")
    with raises(TypeError):
        validate.positive_nonzero_int(1.2)


def test_number_in_interval():
    validate.number_in_interval(3, 2, 4, lower_open=True, upper_open=True)
    validate.number_in_interval(3, 3, 4, lower_open=False, upper_open=True)
    validate.number_in_interval(3, 2, 3, lower_open=True, upper_open=False)

    validate.number_in_interval(-3, -4, 4, lower_open=True, upper_open=True)
    validate.number_in_interval(-3, -3, 4, lower_open=False, upper_open=True)
    validate.number_in_interval(3, -2, 3, lower_open=True, upper_open=False)

    validate.number_in_interval(3, -2, 4, lower_open=True, upper_open=True)
    validate.number_in_interval(-3, -3, 4, lower_open=False, upper_open=True)
    validate.number_in_interval(3, -2, 3, lower_open=True, upper_open=False)

    with raises(ValueError):
        validate.number_in_interval(5, 3, 4, lower_open=True, upper_open=True)
    with raises(ValueError):
        validate.number_in_interval(2, 3, 4, lower_open=True, upper_open=True)
    with raises(ValueError):
        validate.number_in_interval(3, 3, 4, lower_open=True, upper_open=True)
    with raises(ValueError):
        validate.number_in_interval(3, 2, 3, lower_open=True, upper_open=True)
    with raises(TypeError):
        validate.number_in_interval("5", 2, 4, lower_open=True, upper_open=True)
    with raises(TypeError):
        validate.number_in_interval(2, "5", 4, lower_open=True, upper_open=True)
    with raises(TypeError):
        validate.number_in_interval(2, 1, "5", lower_open=True, upper_open=True)


def test_multiplicity_any():
    validate.multiplicity_any(1)
    validate.multiplicity_any(2)
    validate.multiplicity_any("multiples")
    validate.multiplicity_any("all")

    with raises(ValueError):
        validate.multiplicity_any(0)
    with raises(ValueError):
        validate.multiplicity_any(-1)
    with raises(ValueError):
        validate.multiplicity_any("2")

    with raises(TypeError):
        validate.multiplicity_any([])


def test_multiplicity_any_singular_or_all_multiples():
    validate.multiplicity_any_singular_or_all_multiples(1)
    validate.multiplicity_any_singular_or_all_multiples(2)
    validate.multiplicity_any_singular_or_all_multiples("multiples")

    with raises(ValueError):
        validate.multiplicity_any_singular_or_all_multiples("all")
    with raises(ValueError):
        validate.multiplicity_any_singular_or_all_multiples(0)
    with raises(ValueError):
        validate.multiplicity_any_singular_or_all_multiples(-1)
    with raises(ValueError):
        validate.multiplicity_any_singular_or_all_multiples("2")

    with raises(TypeError):
        validate.multiplicity_any_singular_or_all_multiples([])


def test_multiplicity_singular_two_or_greater():
    validate.multiplicity_singular_two_or_greater(2)
    validate.multiplicity_singular_two_or_greater(3)
    with raises(Exception):
        validate.multiplicity_singular_two_or_greater("1")
    with raises(Exception):
        validate.multiplicity_singular_two_or_greater(0)
    with raises(Exception):
        validate.multiplicity_singular_two_or_greater(-1)
    with raises(Exception):
        validate.multiplicity_singular_two_or_greater(1)
    with raises(Exception):
        validate.multiplicity_singular_two_or_greater(None)


def test_multiplicity_singular_one_or_greater():
    validate.multiplicity_singular_one_or_greater(1)
    validate.multiplicity_singular_one_or_greater(2)
    with raises(Exception):
        validate.multiplicity_singular_one_or_greater(0)
    with raises(Exception):
        validate.multiplicity_singular_one_or_greater(-3)
    with raises(Exception):
        validate.multiplicity_singular_one_or_greater("3")


def test_multiplicity_non_singles():
    m1 = validate.multiplicity_non_singles(2)
    m2 = validate.multiplicity_non_singles(12)
    m3 = validate.multiplicity_non_singles("multiples")

    assert m1 == 2
    assert m2 == 12
    assert m3 == "multiples"

    with raises(ValueError):
        validate.multiplicity_non_singles(1)
    with raises(ValueError):
        validate.multiplicity_non_singles(-1)
    with raises(ValueError):
        validate.multiplicity_non_singles(0)
    with raises(ValueError):
        validate.multiplicity_non_singles("string")
    with raises(ValueError):
        validate.multiplicity_non_singles(True)
    with raises(ValueError):
        validate.multiplicity_non_singles([0, 1])


def test_choice():
    validate.choice(1, (1, 2, 3))
    validate.choice("apple", ("orange", "apple", "bannana"))
    with raises(Exception):
        validate.choice("a", ("b", "c", "d"))
    with raises(Exception):
        validate.choice(5, (1, 2, 6))


def test_all_positive_nonzero():
    validate.all_positive_nonzero((1, 2, 6, 3))
    with raises(ValueError):
        validate.all_positive_nonzero((1, 2, 6, -3))


