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

import apav.core.multipleevent as me
import pytest
from pytest import raises
import apav
import numpy as n


def test_npars_in_multievents():
    with raises(ValueError):
        me.pairs_per_multiplicity(0)
    with raises(ValueError):
        me.pairs_per_multiplicity(1)

    assert me.pairs_per_multiplicity(2) == 1
    assert me.pairs_per_multiplicity(3) == 3
    assert me.pairs_per_multiplicity(4) == 6
    assert me.pairs_per_multiplicity(5) == 10
    assert me.pairs_per_multiplicity(6) == 15

    with raises(ValueError):
        me.pairs_per_multiplicity(0)
    with raises(ValueError):
        me.pairs_per_multiplicity(1)
    with raises(TypeError):
        me.pairs_per_multiplicity("multiples")


class TestMultipleEventExtractor:
    def test_params(self, doubles_roi):
        mevents = me.MultipleEventExtractor(doubles_roi, 2, ((4, 56), (57, 90)))
        assert mevents.multiplicity == 2
        assert mevents.roi == doubles_roi

        me.MultipleEventExtractor(doubles_roi, "multiples")

        with raises(ValueError):
            me.MultipleEventExtractor(doubles_roi, 1)
        with raises(ValueError):
            me.MultipleEventExtractor(doubles_roi, 2, ((45, 12), (56, 399)))

    def test_n_pairs(self, doubles_roi, singles_roi, triples_roi):
        mevents = me.MultipleEventExtractor(doubles_roi, 2)
        assert mevents.n_pairs == 3

        mevents = me.MultipleEventExtractor(singles_roi, 2)
        assert mevents.n_pairs == 0

        mevents = me.MultipleEventExtractor(triples_roi, 2)
        assert mevents.n_pairs == 3

        mevents = me.MultipleEventExtractor(triples_roi, 3)
        assert mevents.n_pairs == me.pairs_per_multiplicity(3) * 2

    def test_extents(self, doubles_roi, triples_roi):
        mevents = me.MultipleEventExtractor(doubles_roi, 2)
        assert mevents.n_pairs == 3

        with raises(Exception):
            me.MultipleEventExtractor(doubles_roi, 2, extents=(2, 100))
        with raises(Exception):
            me.MultipleEventExtractor(doubles_roi, 2, extents=10)
        with raises(Exception):
            me.MultipleEventExtractor(doubles_roi, 2, extents=((2, 100), (-10, 49)))

        mevents = me.MultipleEventExtractor(doubles_roi, 2, extents=((3, 13), (3, 13)))
        assert mevents.n_pairs == 2

        mevents = me.MultipleEventExtractor(doubles_roi, 2, extents=((0, 2), (0, 2)))
        assert mevents.n_pairs == 1

        mevents = me.MultipleEventExtractor(triples_roi, 3, extents=((1, 6), (1, 6)))
        assert mevents.n_pairs == 6

        mevents = me.MultipleEventExtractor(triples_roi, "multiples", extents=((1, 6), (1, 6)))
        assert mevents.n_pairs == 8

        mevents = me.MultipleEventExtractor(triples_roi, "multiples", extents=((1, 3), (1, 6)))
        assert mevents.n_pairs == 4

        mevents = me.MultipleEventExtractor(triples_roi, "multiples", extents=((4, 10), (1, 12)))
        assert mevents.n_pairs == 4

    def test_pairs(self, doubles_roi, triples_roi):
        mevents = me.MultipleEventExtractor(doubles_roi, 2)
        pairs = n.array([[1, 1.1],
                         [5.6, 12],
                         [3.4, 3.5]])
        assert n.allclose(mevents.pairs, pairs)

        mevents = me.MultipleEventExtractor(triples_roi, 2)
        assert n.allclose(mevents.pairs, pairs)

        mevents = me.MultipleEventExtractor(triples_roi, 3)
        pairs = n.array([[1, 2],
                         [1, 3],
                         [2, 3],
                         [4, 5],
                         [4, 6],
                         [5, 6]])
        assert n.allclose(mevents.pairs, pairs)

    def test_pair_indices(self, doubles_roi, triples_roi):
        mevents = me.MultipleEventExtractor(doubles_roi, 2)
        idx = n.array([[0, 1],
                       [3, 4],
                       [5, 6]])
        assert n.array_equal(mevents.pair_indices, idx)

        mevents = me.MultipleEventExtractor(triples_roi, 3)
        idx = n.array([[3, 4],
                       [3, 5],
                       [4, 5],
                       [10, 11],
                       [10, 12],
                       [11, 12]])
        assert n.array_equal(mevents.pair_indices, idx)
