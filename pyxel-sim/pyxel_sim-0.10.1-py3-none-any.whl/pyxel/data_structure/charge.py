#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel Charge class to generate electrons or holes inside detector."""

import typing as t

import numpy as np
import pandas as pd
from astropy.units import cds

from pyxel.data_structure import Particle

cds.enable()


class Charge(Particle):
    """Charged particle class defining and storing information of all electrons and holes.

    Properties stored are: charge, position, velocity, energy.
    """

    def __init__(self):
        # TODO: The following line is not really needed
        super().__init__()
        self.nextid = 0  # type: int

        self.columns = (
            "charge",
            "number",
            "init_energy",
            "energy",
            "init_pos_ver",
            "init_pos_hor",
            "init_pos_z",
            "position_ver",
            "position_hor",
            "position_z",
            "velocity_ver",
            "velocity_hor",
            "velocity_z",
        )  # type: t.Tuple[str, ...]

        self.EMPTY_FRAME = pd.DataFrame(
            columns=self.columns, dtype=float
        )  # type: pd.DataFrame

        self.frame = self.EMPTY_FRAME.copy()  # type: pd.DataFrame

    def add_charge(
        self,
        *,
        particle_type: str,  # TODO: Use Enum
        particles_per_cluster: t.Union[t.Sequence[int], np.ndarray],
        init_energy: t.Union[t.Sequence[float], np.ndarray],
        init_ver_position: t.Union[t.Sequence[float], np.ndarray],
        init_hor_position: t.Union[t.Sequence[float], np.ndarray],
        init_z_position: t.Union[t.Sequence[float], np.ndarray],
        init_ver_velocity: np.ndarray,
        init_hor_velocity: np.ndarray,
        init_z_velocity: np.ndarray,
    ) -> None:
        """Create new charge or group of charge inside the detector stored in a pandas DataFrame.

        :param particle_type:
        :param particles_per_cluster:
        :param init_energy:
        :param init_ver_position:
        :param init_hor_position:
        :param init_z_position:
        :param init_ver_velocity:
        :param init_hor_velocity:
        :param init_z_velocity:
        :return:
        """
        if not (
            len(particles_per_cluster)
            == len(init_energy)
            == len(init_ver_position)
            == len(init_ver_velocity)
        ):
            raise ValueError("List arguments have different lengths")

        elements = len(init_energy)

        # check_position(self.detector, init_ver_position, init_hor_position, init_z_position)      # TODO
        # check_energy(init_energy)             # TODO
        # Check if particle number is integer:
        # check_type(particles_per_cluster)      # TODO

        # TODO: particle_type should be a Enum class ?
        if particle_type == "e":
            charge = [-1] * elements  # * cds.e
        elif particle_type == "h":
            charge = [+1] * elements  # * cds.e
        else:
            raise ValueError("Given charged particle type can not be simulated")

        # if all(init_ver_velocity) == 0 and all(init_hor_velocity) == 0 and all(init_z_velocity) == 0:
        #     random_direction(1.0)

        # dict
        new_charge = {
            "charge": charge,
            "number": particles_per_cluster,
            "init_energy": init_energy,
            "energy": init_energy,
            "init_pos_ver": init_ver_position,
            "init_pos_hor": init_hor_position,
            "init_pos_z": init_z_position,
            "position_ver": init_ver_position,
            "position_hor": init_hor_position,
            "position_z": init_z_position,
            "velocity_ver": init_ver_velocity,
            "velocity_hor": init_hor_velocity,
            "velocity_z": init_z_velocity,
        }

        new_charge_df = pd.DataFrame(
            new_charge, index=range(self.nextid, self.nextid + elements)
        )
        self.nextid = self.nextid + elements
        self.frame = self.frame.append(new_charge_df, sort=False)
