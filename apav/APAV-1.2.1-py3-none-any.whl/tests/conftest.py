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

from pytest import fixture
import numpy as n

import apav as ap
import apav.analysis.massspectrum as ms
from apav.utils.helpers import data_path


@fixture()
def singles_roi() -> ap.Roi:
    """
    Fixture roi containing only single multiplicity ions
    """
    ipp = n.array([1, 1, 1, 1, 1, 1, 1])
    mass = n.array([1, 1.1, 3, 5.6, 12, 3.4, 3.5])
    xyz = n.array([[1, 0, 0],
                   [1, 1, 0],
                   [4, 2, 1],
                   [4, 7, 1],
                   [4, 7, 9],
                   [8, 2, 4],
                   [9, 4, 3]])

    roi = ap.Roi(xyz, mass)
    roi.misc["ipp"] = ipp
    return roi


@fixture()
def doubles_roi() -> ap.Roi:
    """
    Roi fixture containing single and double multiplicity ions
    """
    ipp = n.array([2, 0, 1, 2, 0, 2, 0])
    mass = n.array([1, 1.1, 3, 5.6, 12, 3.4, 3.5])
    xyz = n.array([[1, 0, 0],
                   [1, 1, 0],
                   [4, 2, 1],
                   [4, 7, 1],
                   [4, 7, 9],
                   [8, 2, 4],
                   [9, 4, 3]])

    roi = ap.Roi(xyz, mass)
    roi.misc["ipp"] = ipp
    return roi


@fixture()
def triples_roi() -> ap.Roi:
    """
    Roi fixture containing single, double, and triple multiplicity ions
    """
    ipp = n.array([2, 0,   1, 3, 0, 0, 2,   0,  2,   0,   3, 0, 0])
    mass = n.array([1, 1.1, 3, 1, 2, 3, 5.6, 12, 3.4, 3.5, 4, 5, 6])
    det_x = n.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
    det_y = n.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130])
    tof = n.array([3, 23, 120, 32, 34, 2, 430, 23, 54, 15, 76, 87, 13])
    xyz = n.array([[1, 0, 0],
                   [1, 1, 0],
                   [4, 2, 1],
                   [4, 7, 1],
                   [8, 2, 4],
                   [4, 7, 9],
                   [4, 2, 1],
                   [8, 2, 4],
                   [4, 7, 1],
                   [8, 2, 4],
                   [1, 1, 0],
                   [4, 2, 1],
                   [9, 4, 3]])

    roi = ap.Roi(xyz, mass)
    roi.misc["ipp"] = ipp
    roi.misc["det_x"] = det_x
    roi.misc["det_y"] = det_y
    roi.misc["tof"] = tof
    return roi


@fixture()
def triples_range() -> ap.RangeCollection:
    """
    Synthetic RangeCollection fixture for use with triples_roi
    """
    retn = ap.RangeCollection()
    retn.add(ap.Range("A", (6, 13)))
    retn.add(ap.Range("A2", (0, 3)))
    retn.add(ap.Range("B", (3, 5)))
    retn.add(ap.Range("C", (40, 50)))
    return retn


@fixture(scope="module")
def si_roi() -> ap.Roi:
    roi = ap.Roi.from_epos(data_path("Si.epos"))
    return roi


@fixture(scope="module")
def si_range():
    rng = ap.RangeCollection.from_rrng(data_path("Si.RRNG"))
    return rng


@fixture(scope="module")
def si_ranged_ms(si_range, si_roi):
    mass = ms.RangedMassSpectrum(si_roi, si_range)
    return mass


@fixture()
def si_ranged_ms_plot(si_ranged_ms):
    plot = si_ranged_ms.plot()
    return plot
