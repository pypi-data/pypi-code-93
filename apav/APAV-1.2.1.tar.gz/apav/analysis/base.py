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
from apav.utils.validate import AbstractMethodError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apav.core.roi import Roi


class AnalysisBase:
    """
    Superclass for analysis classes
    """
    def __init__(self, roi: Roi):
        self.__roi = roi
        self._update_suppress = True

    @property
    def roi(self):
        return self.__roi

    def _process(self):
        """
        Method to perform the calculation for the given analysis, must be overwritten
        """
        raise AbstractMethodError()
