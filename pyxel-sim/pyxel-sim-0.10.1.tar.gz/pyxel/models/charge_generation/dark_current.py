#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Simple model to generate charges due to dark current process."""
import logging

import numpy as np

from pyxel.detectors import CMOS


# TODO: Fix this
# @validators.validate
# @config.argument(name='detector', label='', units='', validate=checkers.check_type(CMOS))
def dark_current_rule07(detector: CMOS) -> None:
    """Generate charge from dark current process.

    :param detector: Pyxel Detector object
    TODO: investigate on the knee of rule07 for higher 1/le*T values
    """
    logging.info("")
    geo = detector.geometry
    temperature = detector.environment.temperature
    cutoff = detector.characteristics.cutoff

    amp_to_eps = 6.242e18  # conversion factor from Ampere to Electrons per second
    um2_to_cm2 = 1.0e-8
    conversion_factor = amp_to_eps * um2_to_cm2

    # pitch = 18              # um
    # Rule 07 empirical model parameters
    j0 = 8367.000019  # A/cm**2
    c = -1.162972237
    q = 1.602176624e-19  # Elementary charge (Coulomb)
    k = 1.38064852e-23  # Boltzmann constant (m2 kg s-2 K-1)

    def lambda_e(lambda_cutoff: float) -> float:
        """Compute lambda_e.

        :param lambda_cutoff: (int) Cut-off wavelength of the detector
        """
        lambda_scale = 0.200847413  # um
        lambda_threshold = 4.635136423  # um
        pwr = 0.544071282
        if lambda_cutoff < lambda_threshold:
            le = lambda_cutoff / (
                1
                - ((lambda_scale / lambda_cutoff) - (lambda_scale / lambda_threshold))
                ** pwr
            )
        else:
            le = lambda_cutoff
        return le

    # Rule07
    j = j0 * np.exp(c * (1.24 * q / k) * 1.0 / (lambda_e(cutoff) * temperature))
    dark = j * conversion_factor * geo.pixel_horz_size * geo.pixel_vert_size
    # The number of charge generated with Poisson distribution using rule07 empiric law for lambda
    charge_number = np.random.poisson(dark, size=(geo.row, geo.col))

    charge_number = charge_number.flatten()
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
