#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel photon generator models: photon shot noise."""
import typing as t

import numpy as np

from pyxel.detectors import Detector


# TODO: Fix this
# @validators.validate
# @config.argument(name='seed', label='random seed', units='', validate=checkers.check_type(int))
def shot_noise(detector: Detector, random_seed: t.Optional[int] = None) -> None:
    """Add shot noise to the number of photon per pixel.

    :param detector: Pyxel Detector object
    :param random_seed: int seed
    """
    if random_seed:
        np.random.seed(random_seed)

    detector.photon.array = np.random.poisson(lam=detector.photon.array)
