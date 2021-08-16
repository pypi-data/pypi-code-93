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
Geometry utilities.

This module contains functions that manipulate geometry information.
"""
from __future__ import absolute_import, division, print_function

from typing import Any, Dict, Tuple  # pylint: disable=unused-import

import numpy

from cfelpyutils import named_tuples


def compute_pix_maps(geometry):
    # type: (Dict[str, Any]) -> PixelMaps
    """
    Computes pixel maps from CrystFEL geometry information.

    This function takes as input some geometry information read from a `CrystFEL
    <http://www.desy.de/~twhite/crystfel/manual-crystfel_geometry.html>`_ file, and
    returns a set of pre-computed pixel maps.

    The origin and the orientation of the reference system for the pixel maps are set
    according to the same conventions as CrystFEL:

    * The center of the reference system is the beam interaction point.

    * +z is the beam direction, and points along the beam (i.e. away from the source).

    * +y points towards the zenith (ceiling).

    * +x completes the right-handed coordinate system.

    Arguments:

        geometry (Dict[str, Any]): a CrystFEL geometry object (A dictionary returned by
            the :func:`~cfelpyutils.crystfel_utils.load_crystfel_geometry` function).

    Returns:

        :class:`~cfelpyutils.named_tuples.PixelMaps`: a named tuple storing the the
        pixel maps.
    """
    max_fs_in_slab = numpy.array(
        [geometry["panels"][k]["max_fs"] for k in geometry["panels"]]
    ).max()
    max_ss_in_slab = numpy.array(
        [geometry["panels"][k]["max_ss"] for k in geometry["panels"]]
    ).max()

    x_map = numpy.zeros(
        shape=(max_ss_in_slab + 1, max_fs_in_slab + 1), dtype=numpy.float32
    )
    y_map = numpy.zeros(
        shape=(max_ss_in_slab + 1, max_fs_in_slab + 1), dtype=numpy.float32
    )
    z_map = numpy.zeros(
        shape=(max_ss_in_slab + 1, max_fs_in_slab + 1), dtype=numpy.float32
    )

    # Iterates over the panels. For each panel, determines the pixel indices, then
    # computes the x,y vectors. Finally, copies the panel pixel maps into the
    # detector-wide pixel maps.
    for pan in geometry["panels"]:

        if "clen" in geometry["panels"][pan]:
            pan_clen = geometry["panels"][pan]["clen"]
        else:
            pan_clen = 0.0

        ss_grid, fs_grid = numpy.meshgrid(
            numpy.arange(
                geometry["panels"][pan]["max_ss"]
                - geometry["panels"][pan]["min_ss"]
                + 1
            ),
            numpy.arange(
                geometry["panels"][pan]["max_fs"]
                - geometry["panels"][pan]["min_fs"]
                + 1
            ),
            indexing="ij",
        )
        y_panel = (
            ss_grid * geometry["panels"][pan]["ssy"]
            + fs_grid * geometry["panels"][pan]["fsy"]
            + geometry["panels"][pan]["cny"]
        )
        x_panel = (
            ss_grid * geometry["panels"][pan]["ssx"]
            + fs_grid * geometry["panels"][pan]["fsx"]
            + geometry["panels"][pan]["cnx"]
        )
        x_map[
            geometry["panels"][pan]["min_ss"] : geometry["panels"][pan]["max_ss"] + 1,
            geometry["panels"][pan]["min_fs"] : geometry["panels"][pan]["max_fs"] + 1,
        ] = x_panel
        y_map[
            geometry["panels"][pan]["min_ss"] : geometry["panels"][pan]["max_ss"] + 1,
            geometry["panels"][pan]["min_fs"] : geometry["panels"][pan]["max_fs"] + 1,
        ] = y_panel
        z_map[
            geometry["panels"][pan]["min_ss"] : geometry["panels"][pan]["max_ss"] + 1,
            geometry["panels"][pan]["min_fs"] : geometry["panels"][pan]["max_fs"] + 1,
        ] = pan_clen

    r_map = numpy.sqrt(numpy.square(x_map) + numpy.square(y_map))
    phi_map = numpy.arctan2(y_map, x_map)

    return named_tuples.PixelMaps(x_map, y_map, z_map, r_map, phi_map)


def compute_visualization_pix_maps(geometry):
    # type: (Dict[str, Any]) -> PixelMaps
    """
    Computes pixel maps for data visualization from CrystFEL geometry information.

    This function takes as input some geometry information read from a `CrystFEL
    <http://www.desy.de/~twhite/crystfel/manual-crystfel_geometry.html>`_ file, and
    returns a set of pre-computed pixel maps that can be used to display data in an
    ImageView widget (from the `PyQtGraph <http://pyqtgraph.org/>`_ library).

    These pixel maps are different from the ones generated by the
    :func:`~compute_pix_maps` function. The main differences are:

    * The origin of the reference system is not the beam interaction point, but the top
      left corner of the array used to visualize the data.

    * Only the x and y pixel maps are available. The other entries in the returned
      named tuple (z, r and phi) are set to None.

    Arguments:

        geometry (Dict[str, Any]): a CrystFEL geometry object (A dictionary returned by
            the :func:`~cfelpyutils.crystfel_utils.load_crystfel_geometry` function).

    Returns:

        :class:`PixelMaps`: a named tuple with the pixel maps.
    """
    # Shifts the origin of the reference system from the beam position to the top-left
    # of the image that will be displayed. Computes the size of the array needed to
    # display the data, then use this information to estimate the magnitude of the
    # shift.
    pixel_maps = compute_pix_maps(geometry)
    x_map, y_map = pixel_maps.x, pixel_maps.y
    y_minimum = 2 * int(max(abs(y_map.max()), abs(y_map.min()))) + 2
    x_minimum = 2 * int(max(abs(x_map.max()), abs(x_map.min()))) + 2
    min_shape = (y_minimum, x_minimum)
    new_x_map = (
        numpy.array(object=pixel_maps.x, dtype=numpy.int) + min_shape[1] // 2 - 1
    )
    new_y_map = (
        numpy.array(object=pixel_maps.y, dtype=numpy.int) + min_shape[0] // 2 - 1
    )
    return named_tuples.PixelMaps(new_x_map, new_y_map, None, None, None)


def apply_geometry_to_data(data, geometry):
    # type: (numpy.ndarray, Dict[str, Any]) -> numpy.ndarray
    """
    Applies CrystFEL geometry information to some data.

    This function takes as input some geometry information read from a `CrystFEL
    <http://www.desy.de/~twhite/crystfel/manual-crystfel_geometry.html>`_ file, and
    some data on which to apply the information. It returns an array that can be
    displayed using libraries like `matplotlib <https://matplotlib.org/>`_ or
    `PyQtGraph <http://pyqtgraph.org/>`_.

    The shape of the returned array is big enough to display all the pixel values in
    the input data, and is symmetric around the center of the reference system
    (i.e: the beam interaction point).

    These restrictions often cause the returned array to be bigger than the minimum
    size needed to store the physical layout of the pixels in the detector,
    particularly if the detector is not centered at the beam interaction point.

    Arguments:

        data (numpy.ndarray): the data on which the geometry information should be
            applied.

        geometry (Dict[str, Any]): a CrystFEL geometry object (A dictionary returned by
            the :func:`~cfelpyutils.crystfel_utils.load_crystfel_geometry` function).

    Returns:

        numpy.ndarray: an array containing the data with the geometry information
        applied.
    """
    pixel_maps = compute_pix_maps(geometry)
    x_map, y_map = pixel_maps.x, pixel_maps.y
    y_minimum = 2 * int(max(abs(y_map.max()), abs(y_map.min()))) + 2
    x_minimum = 2 * int(max(abs(x_map.max()), abs(x_map.min()))) + 2
    min_shape = (y_minimum, x_minimum)
    visualization_array = numpy.zeros(min_shape, dtype=float)
    visual_pixel_maps = compute_visualization_pix_maps(geometry)
    visualization_array[
        visual_pixel_maps.y.flatten(), visual_pixel_maps.x.flatten()
    ] = data.ravel().astype(visualization_array.dtype)
    return visualization_array
