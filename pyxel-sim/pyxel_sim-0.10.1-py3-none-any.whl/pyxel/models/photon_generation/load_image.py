#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel photon generator models."""
import typing as t
from pathlib import Path

import numpy as np

from pyxel import inputs_outputs
from pyxel.data_structure import Photon
from pyxel.detectors import Detector


# TODO: Fix this
# @validators.validate
# @config.argument(name='image_file', label='fits file', validate=check_path)
# @config.argument(name='fit_image_to_det', label='fitting image to detector', validate=check_type(bool))
# @config.argument(name='convert_to_photons', label='convert ADU values to photon numbers', validate=check_type(bool))
def load_image(
    detector: Detector,
    image_file: str,
    fit_image_to_det: bool = False,
    position: t.Tuple[int, int] = (0, 0),  # TODO Too many arguments
    convert_to_photons: bool = False,
) -> None:
    r"""Load FITS file as a numpy array and add to the detector as input image.

    :param detector: Pyxel Detector object
    :param image_file: path to FITS image file
    :param fit_image_to_det: fitting image to detector shape (Geometry.row, Geometry.col)
    :param position: indices of starting row and column, used when fitting image to detector
    :param convert_to_photons: if ``True``, the model converts the values of loaded image array from ADU to
        photon numbers for each pixel using the Photon Transfer Function:
        :math:`PTF = QE \cdot \eta \cdot S_{v} \cdot amp \cdot a_{1} \cdot a_{2}`
    """
    filename = Path(image_file).expanduser().resolve()

    if not Path(filename).exists():
        raise FileNotFoundError(f"Image file '{filename}' does not exist !")

    image = inputs_outputs.load_image(filename)  # type: np.ndarray

    if fit_image_to_det:
        geo = detector.geometry
        position_y, position_x = position

        image = image[
            slice(position_y, position_y + geo.row),
            slice(position_x, position_x + geo.col),
        ]

    detector.input_image = image
    photon_array = image

    if convert_to_photons:
        cht = detector.characteristics
        photon_array = photon_array / (
            cht.qe * cht.eta * cht.sv * cht.amp * cht.a1 * cht.a2
        )

    detector.photon = Photon(photon_array)
