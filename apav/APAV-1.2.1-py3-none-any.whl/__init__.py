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

from importlib import metadata

from apav.core.roi import Roi, RoiSphere, RoiCylinder, RoiRectPrism
from apav.core.range import RangeCollection, Range
from apav.core.isotopic import Isotope, IsotopeSeries, Ion
from apav.core.multipleevent import MultipleEventExtractor
from apav.utils import validate

__version__ = metadata.version(__name__)


# Define some convenience functions for loading data

def load_rrng(filepath: str) -> RangeCollection:
    validate.file_exists(filepath)
    return RangeCollection.from_rrng(filepath)


def load_rng(filepath: str) -> RangeCollection:
    validate.file_exists(filepath)
    return RangeCollection.from_rng(filepath)


def load_pos(filepath: str) -> Roi:
    validate.file_exists(filepath)
    return Roi.from_pos(filepath)


def load_epos(filepath: str) -> Roi:
    validate.file_exists(filepath)
    return Roi.from_epos(filepath)


def load_ato(filepath: str) -> Roi:
    validate.file_exists(filepath)
    return Roi.from_ato(filepath)


def load_apt(filepath: str) -> Roi:
    validate.file_exists(filepath)
    return Roi.from_apt(filepath)
