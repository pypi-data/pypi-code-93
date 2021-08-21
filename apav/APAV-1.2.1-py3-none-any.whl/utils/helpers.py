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
from typing import TYPE_CHECKING
import os
from os.path import join

import numpy as n
from numba import njit

from apav.qt import *
from apav.utils import validate
from apav.utils.hinting import *

if TYPE_CHECKING:
    from apav.analysis.base import AnalysisBase

_thispath = os.path.abspath(os.path.dirname(__file__))

paths = {"toplevel": join(_thispath, "..", ".."),
         "testdata": join(_thispath, "..", "resources", "testdata"),
         "icons": join(_thispath, "..", "resources", "icons")}


unicode_map = {"deg": "\u00B0",
               "degree": "\u00B0",
               "degrees": "\u00B0",
               "angstrom": "\u212B",
               "angstroms": "\u212B",
               "PHI": "\u03D5",
               "phi": "\u03C6",
               "alpha": "\u03B1",
               "BETA": "\u03D0",
               "beta": "\u03B2",
               "gamma": "\u03B3",
               "theta": "\u03B8",
               "mu": "\u03BC",
               "empty": "\u21B5"}

_unit_suffix = {"nm": "nm",
                "nanometer": "nm",
                "nanometers": "nm",
                "pm": "pm",
                "picometer": "pm",
                "picometers": "pm"}


def data_path(filename: str) -> str:
    """
    Get file path for a data in the test data directory
    :param filename: filename
    :return: path to file
    """
    fpath = join(paths["testdata"], filename)
    if not os.path.isfile(fpath):
        raise FileExistsError(f"{filename} does not exist")
    return fpath


def get_icon(name: str):
    path = join(paths["icons"], name)
    if not os.path.isfile(path) and os.path.exists(path):
        raise FileNotFoundError(f"Icon {name} was not found")
    return QIcon(path)


def make_action(text: str, slot, icon: str = None, tooltip: str = None, checked=None):
    retn = QAction()
    retn.setText(text)
    if icon is not None:
        retn.setIcon(get_icon(icon))
    if tooltip is not None:
        retn.setToolTip(tooltip)
    if isinstance(checked, bool):
        retn.setCheckable(True)
        retn.setChecked(checked)
    retn.triggered.connect(slot)
    return retn


def intervals_intersect(minmax1: Tuple[float, float], minmax2: Tuple[float, float]) -> bool:
    """
    Determine if two 1-dimensional intervals [first, last) overlap
    """
    if minmax2[0] <= minmax1[0] < minmax2[1]:
        return True
    elif minmax1[0] <= minmax2[0] < minmax1[1]:
        return True
    return False


@njit()
def minmax(ary) -> Tuple[float, float]:
    """
    Fast function for finding the min and max values of an array
    """
    maximum = ary[0]
    minimum = ary[0]
    for i in ary[1:]:
        if i > maximum:
            maximum = i
        elif i < minimum:
            minimum = i
    return minimum, maximum


def mass2tof(mass: float, calib: float):
    """
    Convert mass/charge (Da) to time of flight (ns) via m = kt^2. the calibration coefficient may be found in
    IVAS root logs.

    :param mass: mass/charge ratio
    :param calib: calibration coefficient
    :return:
    """
    validate.positive_nonzero_number(mass)
    validate.positive_nonzero_number(calib)
    return n.sqrt(mass/calib)


def unique_int8(array: ndarray) -> ndarray:
    """
    Faster implementation of numpy.unique for int8 or uint8 dtype
    :param array: input array
    """
    if array.dtype in (n.int8, n.uint8):
        return n.argwhere(n.bincount(array.ravel()) != 0).ravel()
    else:
        return n.unique(array)


def unit_string(unit: str, prefix_space: bool = False) -> str:
    """
    Make a unit string, i.e. angstrom symbol

    :param unit: unit
    :param prefix_space: add a space before the prefix
    :return: unit string
    """
    retn = ""
    if prefix_space is True:
        retn += " "
    try:
        return retn + unicode_map[unit]
    except KeyError:
        return retn + _unit_suffix[unit]


def baseround(x: float, base: bool = 5) -> int:
    """
    Round to given base value
    """
    return int(base * round(float(x)/base))


def isnumber(string: str) -> bool:
    """
    Test if string is a number
    """
    try:
        float(string)
        return True
    except ValueError:
        return False


def str2number(string: str):
    """
    Convert a string to a number if possible
    :param string: string
    :return: float or int
    """
    num = float(string)
    if num % 1 == 0:
        return int(num)
    else:
        return num


def dir_path(fpath: str) -> str:
    """
    Convert filepath to directory path
    """
    return os.path.abspath(os.path.dirname(fpath))


def curr_file_path() -> str:
    """
    Current file path
    """
    return os.path.abspath(os.path.dirname(__file__))


_NUMERALS = '0123456789abcdefABCDEF'
_HEXDEC = {v: int(v, 16) for v in (x+y for x in _NUMERALS for y in _NUMERALS)}
LOWERCASE, UPPERCASE = 'x', 'X'


def hex2rgbF(text: str) -> tuple:
    """
    Convert a hex/HTML color code to RGB fractions
    """
    text = text.replace("#", "")
    rgb = _HEXDEC[text[0:2]], _HEXDEC[text[2:4]], _HEXDEC[text[4:6]]
    return tuple([i/255. for i in rgb])


def subscript_num_html(txt: str) -> str:
    """
    Subscript in html format
    :param txt:
    """
    return "<sub>{}</sub>".format(txt)


def subscript_num(number: int) -> str:
    """
    Get the unicode characters for making a numerical subscript
    """
    umap = {"0": u"\u2080",
            "1": u"\u2081",
            "2": u"\u2082",
            "3": u"\u2083",
            "4": u"\u2084",
            "5": u"\u2085",
            "6": u"\u2086",
            "7": u"\u2087",
            "8": u"\u2088",
            "9": u"\u2089"}
    numstr = str(number)
    retn = ""
    for i in numstr:
        retn += umap[i]

    return retn


def superscript_num(number: int) -> str:
    """
    Get the unicode characters for making a numerical superscript
    """
    umap = {"0": u"\u2070",
            "1": u"\u00B9",
            "2": u"\u00B2",
            "3": u"\u00B3",
            "4": u"\u2074",
            "5": u"\u2075",
            "6": u"\u2076",
            "7": u"\u2077",
            "8": u"\u2078",
            "9": u"\u2079"}
    numstr = str(number)
    retn = ""
    for i in numstr:
        retn += umap[i]
        
    return retn


class modifying:
    """
    Context manager for making changes to Analysis objects without unnecessary calculations. This may be
    useful when dealing with large data and multiple changes need to be made to the analysis, and you do not want to
    reuse the original analysis object. The analysis is automatically recalculated once the context manager exits.

    This is located here to avoid circular imports in the analysis-plotting namespaces.

    The below example code loads a large Roi, calculates a correlation histogram, then modifies 3 of the correlation
    histograms parameters. The correlation histogram is only computed 2 time, at instantiation and when the context
    manager exits.

    >>> from apav.analysis import CorrelationHistogram
    >>> from apav import Roi
    >>> large_roi = Roi.from_epos("path_to_large_roi.epos")
    >>> hist = CorrelationHistogram(large_roi, extents=((50, 100), (25, 75)), bin_width=0.01)
    >>>
    >>> with modifying(hist) as anl:
    >>>     anl.bin_width = 0.2
    >>>     anl.symmetric=True
    >>>     anl.multiplicity="multiples"
    """

    def __init__(self, analysis: AnalysisBase):
        self.analysis = analysis

    def __enter__(self):
        self.analysis._update_suppress = True
        return self.analysis

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.analysis._update_suppress = False
        self.analysis._process()