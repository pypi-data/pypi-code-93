#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel charge collection model."""
import logging

import numba
import numpy as np

from pyxel.data_structure import Charge
from pyxel.detectors import Detector


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
# TODO: Is it not better/relevant if all models return a new `Detector` ?
#       Therefore the 'input' `Detector` is never modified.
#
#       Example:
#       >>> def simple_collection(detector: Detector) -> Detector:
#       ...     # Create a new object `Detector`.
#       ...     # Note: This is not an expensive 'deep' copy
#       ...     new_detector = detector.copy()
#       ...     # Do something
#       ...     return new_detector
def simple_collection(detector: Detector) -> None:
    """Associate charge with the closest pixel."""
    logging.info("")
    geo = detector.geometry
    array = np.zeros((geo.row, geo.col))

    charge_per_pixel = detector.charge.get_values(quantity="number")
    charge_pos_ver = detector.charge.get_values(quantity="position_ver")
    charge_pos_hor = detector.charge.get_values(quantity="position_hor")

    pixel_index_ver = np.floor_divide(charge_pos_ver, geo.pixel_vert_size).astype(int)
    pixel_index_hor = np.floor_divide(charge_pos_hor, geo.pixel_horz_size).astype(int)

    # Changing = to += since charge dataframe is reset, the pixel array need to be
    # incremented, we can't do the whole operation on each iteration
    detector.pixel.array += df_to_array(
        array, charge_per_pixel, pixel_index_ver, pixel_index_hor
    ).astype(np.int32)


def empty_charge(detector: Detector) -> None:
    """Each time the charges are collected in the pixel, the charge array is reset using Charge().

    This allows to limit memory leaks due to long exposure.
    There will still be a problem for very large charge array due to very high flux
    in simulation.
    """
    detector._charge = Charge()


# TODO: Is it needed not better to first create a copy of 'array' and then work with this copy ??
@numba.jit(nopython=True)
def df_to_array(
    array: np.ndarray,
    charge_per_pixel: list,
    pixel_index_ver: list,
    pixel_index_hor: list,
) -> np.ndarray:
    """TBW."""
    for i, charge_value in enumerate(charge_per_pixel):
        array[pixel_index_ver[i], pixel_index_hor[i]] += charge_value
    return array
