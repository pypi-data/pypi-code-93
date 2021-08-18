#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Fix pattern noise model."""
import logging
import typing as t
from pathlib import Path

import numpy as np

from pyxel.detectors import Detector, Geometry


# TODO: Fix this
# @validators.validate
# @config.argument(name='', label='', units='', validate=)
def fix_pattern_noise(
    detector: Detector, pixel_non_uniformity: t.Union[str, Path, None] = None
) -> None:
    """Add fix pattern noise caused by pixel non-uniformity during charge collection.

    Parameters
    ----------
    detector : Detector
        Pyxel Detector object.
    pixel_non_uniformity : str or Path
        path to an ascii file with and array.
    """
    geo = detector.geometry  # type: Geometry

    if pixel_non_uniformity is not None:
        if ".npy" in str(pixel_non_uniformity):
            pnu = np.load(pixel_non_uniformity)
        else:
            pnu = np.loadtxt(pixel_non_uniformity)
    else:
        filename = Path("data/pixel_non_uniformity.npy").resolve()

        if filename.exists():
            logging.warning(
                "'pixel_non_uniformity' file is not defined, "
                "using array from file: %s",
                filename,
            )
            pnu = np.load(filename)
        else:
            logging.warning(
                "'pixel_non_uniformity' file is not defined, "
                "generated random array to file: %s",
                filename,
            )

            # pnu = 0.99 + np.random.random((geo.row, geo.col)) * 0.02
            pnu = np.random.normal(loc=1.0, scale=0.03, size=(geo.row, geo.col))
            np.save(filename, pnu)

    pnu = pnu.reshape((geo.row, geo.col))

    detector.pixel.array = detector.pixel.array.astype(np.float64) * pnu  # TODO: dtype!
