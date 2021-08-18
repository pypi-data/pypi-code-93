#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel Image class."""

from typing import TYPE_CHECKING

import numpy as np
from astropy.units import cds

from pyxel.data_structure import Array

if TYPE_CHECKING:
    from pyxel.detectors import Geometry

cds.enable()


class Image(Array):
    """
    Image class defining and storing information of detector image.

    Accepted array types: np.uint16, np.uint32, np.uint64
    """

    EXP_TYPE = np.uint
    TYPE_LIST = (np.uint16, np.uint32, np.uint64, np.float16, np.float32, np.float64)

    def __init__(self, geo: "Geometry"):
        new_array = np.zeros((geo.row, geo.col), dtype=self.EXP_TYPE)

        super().__init__(new_array)
