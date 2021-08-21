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

import numpy as n

import apav.core.roi as apt
import apav.core.histogram

from pytest import raises


def test_histogram1d():
    x = n.array([1.5, 2.5, 4.25, 4.75])
    data, edges = apav.core.histogram.histogram1d(x, 1, (1, 5))
    assert n.allclose(data, n.array([1, 1, 0, 2]))
    assert n.allclose(edges, n.array([1.5, 2.5, 3.5, 4.5]))

    with raises(Exception):
        apav.core.histogram.centers2edges(n.arange(9).reshape([3, 3]), 0.1)


def test_histogram2d():
    x = n.random.randn(100)
    y = n.random.randn(100)

    bwidth = 0.01
    ext = ((-0.2, 1), (0, 1))
    nbinsx = int((ext[0][1]-ext[0][0])/bwidth)
    nbinsy = int((ext[1][1]-ext[1][0])/bwidth)

    hist1 = apav.core.histogram.histogram2d(x, y, ext, (nbinsx, nbinsy))
    hist2 = apav.core.histogram.histogram2d_binwidth(x, y, ext, bwidth)
    assert n.allclose(hist1, hist2)
