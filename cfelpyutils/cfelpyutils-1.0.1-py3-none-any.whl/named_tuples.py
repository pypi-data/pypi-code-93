# This file is part of CFELPyUtils.
#
# CFELPyUtils is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# CFELPyUtils is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with OnDA. If
# not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014-2019 Deutsches Elektronen-Synchrotron DESY,
# a research centre of the Helmholtz Association.
"""
CFELPyUtils named tuples.

This module contains a collection of named tuples used throughout the CFELPyUtils
library.
"""
import collections

PixelMaps = collections.namedtuple("PixelMaps", ["x", "y", "z", "r", "phi"])
"""
Pixel maps that store geometry information.

Arguments:

    x (numpy.ndarray): pixel map for the x coordinate.

    y (numpy.ndarray): pixel map for the y coordinate.

    z (numpy.ndarray): pixel map for the z coordinate.

    r (numpy.ndarray): pixel map storing the distance of each pixel from the center of
        the reference system.

    phi (numpy.ndarray): pixel map storing the amplitude of the angle between each
       pixel, the center of the reference system, and the x axis.
"""
