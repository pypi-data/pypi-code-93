#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Readout electronics model."""
import logging

from pyxel.detectors import Detector

# from astropy import units as u


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
def simple_amplifier(detector: Detector) -> None:
    """Amplify signal.

    amp - Gain of output amplifier, a1 - Gain of the signal processor

    :param detector: Pyxel Detector object
    """
    logging.info("")
    char = detector.characteristics
    detector.signal.array *= char.amp * char.a1
