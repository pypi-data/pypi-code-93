#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Non-Destructive Readout modes for CMOS-based detectors."""
import logging

from pyxel.detectors import CMOS


# TODO: Fix this
# @validators.validate
# @config.argument(name='mode', label='', units='', validate=check_choices(['uncorrelated', 'CDS', 'Fowler-N', 'UTR']))
# @config.argument(name='fowler_samples', label='', units='', validate=check_type(int))
# @config.argument(name='detector', label='', units='', validate=check_type(CMOS))      # TODO this should be automatic
def non_destructive_readout(detector: CMOS, mode: str, fowler_samples: int = 1) -> None:
    """Non-Destructive Readout modes for CMOS-based detectors.

    :param detector: Pyxel Detector object
    :param mode:
    :param fowler_samples:
    """
    logging.info("")
    if not detector.is_non_destructive_readout or not detector.is_dynamic:
        raise ValueError()

    detector.read_out = False
    if mode == "uncorrelated":
        if detector.time == (detector.end_time - detector.time_step):
            detector.read_out = True
    elif mode == "CDS":
        if detector.time == detector.time_step or detector.time == (
            detector.end_time - detector.time_step
        ):
            detector.read_out = True
    elif mode == "Fowler-N":
        nt = fowler_samples * detector.time_step
        detector.read_out = True
        if nt < detector.time <= detector.end_time - nt:
            detector.read_out = False
    elif mode == "UTR":
        detector.read_out = True
