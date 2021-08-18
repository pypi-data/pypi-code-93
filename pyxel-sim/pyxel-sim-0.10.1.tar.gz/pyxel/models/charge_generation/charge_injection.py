#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel charge injection functions for CCDs."""
import logging
import typing as t

import numpy as np

from pyxel.detectors import CCD


# TODO: Fix this
# @validators.validate
# @config.argument(name='detector', label='', units='', validate=checkers.check_type(CCD))
def charge_blocks(
    detector: CCD,
    charge_level: int,
    block_start: int = 0,
    block_end: t.Optional[int] = None,
) -> None:
    """TBW.

    :param detector:
    :param charge_level:
    :param block_start:
    :param block_end:
    :return:
    """
    logging.info("")
    geo = detector.geometry
    if block_end is None:
        block_end = geo.row

    # all pixels has zero charge by default
    detector_charge = np.zeros((geo.row, geo.col))
    detector_charge[slice(block_start, block_end), :] = charge_level
    charge_number = detector_charge.flatten()
    where_non_zero = np.where(charge_number > 0.0)
    charge_number = charge_number[where_non_zero]
    size = charge_number.size

    init_ver_pix_position = geo.vertical_pixel_center_pos_list()[where_non_zero]
    init_hor_pix_position = geo.horizontal_pixel_center_pos_list()[where_non_zero]

    detector.charge.add_charge(
        particle_type="e",
        particles_per_cluster=charge_number,
        init_energy=np.zeros(size),
        init_ver_position=init_ver_pix_position,
        init_hor_position=init_hor_pix_position,
        init_z_position=np.zeros(size),
        init_ver_velocity=np.zeros(size),
        init_hor_velocity=np.zeros(size),
        init_z_velocity=np.zeros(size),
    )
