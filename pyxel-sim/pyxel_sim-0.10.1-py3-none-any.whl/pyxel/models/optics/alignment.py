#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel photon generator models."""
from pyxel.data_structure import Photon
from pyxel.detectors import Detector


# @pyxel.validate
# @pyxel.argument(name='image_file', label='', validate=check_path)
def alignment(detector: Detector) -> None:
    """Optical alignment.

    :param detector: Pyxel Detector object
    """
    geo = detector.geometry
    rows, cols = detector.photon.array.shape
    row0 = int((rows - geo.row) / 2)
    col0 = int((cols - geo.col) / 2)

    if row0 < 0 or col0 < 0:
        raise ValueError

    aligned_optical_image = detector.photon.array[
        slice(row0, row0 + geo.row), slice(col0, col0 + geo.col)
    ]

    detector.photon = Photon(aligned_optical_image)
