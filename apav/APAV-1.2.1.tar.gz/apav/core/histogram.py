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

import fast_histogram as fh
import numpy as n
from apav.utils.hinting import *

from apav.utils import validate


def centers2edges(data: ndarray, bin_width: float) -> ndarray:
    """
    Convert the x values of a histogram from bin centers to edges. This increases the size of the domain by 1.

    :param data: histogram centers
    :param bin_width: width of the bins
    """
    if len(data.shape) != 1:
        raise AttributeError("Array must be one dimensional to convert centers to edges")

    validate.positive_nonzero_number(bin_width)

    retn = data - bin_width/2
    retn = n.append(retn, retn[-1] + bin_width)
    return retn


def histogram2d(x: ndarray, y: ndarray, extents: (tuple, tuple), bins) -> ndarray:
    """
    Calculate two dimensional histograms by specifying the number of bins.

    :param x: Array 1
    :param y: Array 2
    :param extents: (tuple, tuple) designating range to perform mass_histogram
    :param bins: Number of bins
    """
    counts = fh.histogram2d(x, y, bins, extents)
    return counts


def histogram1d(data: ndarray, bin_width: float, rng: tuple) -> Tuple[ndarray, ndarray]:
    """
    1d mass_histogram that returns array of counts and array of bin centers.

    :param data: data to compute the histogram on
    :param bin_width: bin width of the bins
    :param rng: boundaries of the histogram
    """
    assert len(data.shape) == 1
    edges = n.round(n.arange(rng[0], rng[1] + bin_width, bin_width), 6)
    centers = n.round(n.arange(rng[0]+bin_width/2, rng[1]+bin_width, bin_width), 6)
    nbins = edges.size - 1

    counts = fh.histogram1d(data, nbins, (rng[0], edges[-1]))
    return counts, centers[0:counts.size]


def histogram2d_binwidth(x: ndarray, y: ndarray, extents: (tuple, tuple), bin_width: float = 0.1) -> ndarray:
    """
    Calculate two dimensional histograms by bin width instead of number of bins.

    :param x: Array 1
    :param y: Array 2
    :param extents: (tuple, tuple) designating range to perform mass_histogram
    :param bin_width: Width of the bins in Daltons
    """
    nbinsx = int((extents[0][1] - extents[0][0]) / bin_width)
    nbinsy = int((extents[1][1] - extents[1][0]) / bin_width)

    retn = histogram2d(x, y, extents, (nbinsx, nbinsy))
    return retn
