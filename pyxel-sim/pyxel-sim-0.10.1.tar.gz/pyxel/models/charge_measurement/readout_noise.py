#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Readout noise model."""
import logging
import typing as t

import numpy as np

from pyxel.detectors import Detector

# from astropy import units as u


# @validators.validate
# @config.argument(name='', label='', units='', validate=)


def output_node_noise(
    detector: Detector, std_deviation: float, random_seed: t.Optional[int] = None
) -> None:
    """Adding noise to signal array of detector output node using normal random distribution.

    detector Signal unit: Volt

    :param detector: Pyxel Detector object
    :param std_deviation: standard deviation
    :param random_seed: seed
    """
    logging.info("")
    if random_seed:
        np.random.seed(random_seed)

    signal_mean_array = detector.signal.array.astype("float64")
    sigma_array = std_deviation * np.ones(signal_mean_array.shape)

    signal = np.random.normal(loc=signal_mean_array, scale=sigma_array)

    detector.signal.array = signal
