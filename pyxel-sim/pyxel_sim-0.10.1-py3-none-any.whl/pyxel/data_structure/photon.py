#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel Photon class to generate and track photon."""

import numpy as np
from astropy.units import cds

from pyxel.data_structure import Array

# if TYPE_CHECKING:
#     from pyxel.detectors.geometry import Geometry

cds.enable()


class Photon(Array):
    """Photon class defining and storing information of all photon.

    Accepted array types: np.int32, np.int64, np.uint32, np.uint64, np.float16, np.float32, np.float64
    """

    # TODO: add unit (ph)
    EXP_TYPE = int
    TYPE_LIST = (
        np.int32,
        np.int64,
        np.uint32,
        np.uint64,
        np.float16,
        np.float32,
        np.float64,
    )

    def __init__(self, value: np.ndarray):
        cls_name = self.__class__.__name__  # type: str

        if not isinstance(value, np.ndarray):
            raise TypeError(f"{cls_name} array should be a numpy.ndarray")

        if value.dtype not in self.TYPE_LIST:
            raise TypeError(
                f"Type of {cls_name} array should be a(n) %s" % self.EXP_TYPE.__name__
            )

        self._array = value

    # # TODO: This could be done in '__init__'
    # def new_array(self, new_array: np.ndarray) -> None:
    #     """TBW.
    #
    #     :param new_array:
    #     """
    #     cls_name = self.__class__.__name__  # type: str
    #
    #     if not isinstance(new_array, np.ndarray):
    #         raise TypeError(f'{cls_name} array should be a numpy.ndarray')
    #
    #     if new_array.dtype not in self.TYPE_LIST:
    #         raise TypeError(f'Type of {cls_name} array should be a(n) %s' %
    #                         self.EXP_TYPE.__name__)
    #
    #     self._array = new_array
    #     self.type = new_array.dtype  # TODO: Where is it used ?
