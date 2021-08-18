#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel full well models."""
import logging

from pyxel.detectors import Detector


# @pyxel.validate
# @pyxel.argument(name='', label='', units='', validate=)
def simple_full_well(detector: Detector) -> None:
    """Limiting the amount of charge in pixel due to full well capacity."""
    logging.info("")
    fwc = detector.characteristics.fwc
    if fwc is None:
        raise ValueError("Full Well Capacity is not defined")
    charge_array = detector.pixel.array
    charge_array[charge_array > fwc] = fwc
    detector.pixel.array = charge_array
