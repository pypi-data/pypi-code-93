#    Virtual-IPM is a software for simulating IPMs and other related devices.
#    Copyright (C) 2021  The IPMSim collaboration <https://ipmsim.gitlab.io/>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from anna import parametrize
import numpy as np
import scipy.constants as constants

from virtual_ipm.components import Component
from virtual_ipm.utils.coordinate_transformations import LorentzBoostAlongZ, \
    LorentzBoostAlongZForElectricField
from virtual_ipm.simulation.beams.utils import compute_beta_and_gamma_from_energy
from . import bunch_parameters


@parametrize(
    bunch_parameters.energy,
    bunch_parameters.bunch_population,
    bunch_parameters.particle_type
)
class Bunch(Component):
    """
    This component represents a bunch together with its fields during the simulation.

    It incorporates movement of the bunch through a Lorentz boost of position. Because a beam
    consists of many bunches that share the same shape and fields model those attributes have been
    separated from their position with respect to the chamber. A bunch view incorporates
    this movement and always provides the current bunch attributes.
    """

    CONFIG_PATH = bunch_parameters.CONFIG_PATH

    def __init__(
            self,
            bunch_shape,
            bunch_electric_field_model,
            longitudinal_offset_to_chamber,
            transverse_offset_to_chamber,
            configuration):
        """
        Parameters
        ----------
        bunch_shape : :class:`BunchShape`
        bunch_electric_field_model : :class:`BunchElectricFieldModel`
        longitudinal_offset_to_chamber : float
            The longitudinal offset of the bunch center to the chamber center in units of [s].
        transverse_offset_to_chamber : :class:`~np.ndarray`, shape (2,)
            The transverse offset of the bunch center to the chamber center in units of [m].
        configuration : :class:`ConfigurationAdaptor`
        """
        super().__init__(configuration)
        self._bunch_shape = bunch_shape
        self._bunch_electric_field_model = bunch_electric_field_model
        self._longitudinal_offset = longitudinal_offset_to_chamber
        self._transverse_offset = transverse_offset_to_chamber
        self._population_in_number_of_charges = (
            self._particle_type.charge_number * self._bunch_population
        )
        self._total_charge = self._particle_type.charge * self._bunch_population

        beta, gamma = compute_beta_and_gamma_from_energy(
            self._energy, self._particle_type.rest_energy
        )
        self._beta = beta
        self._gamma = gamma

        self._lorentz_boost = LorentzBoostAlongZ(beta)
        self._lorentz_boost_electric_field = LorentzBoostAlongZForElectricField(beta)

        self.log.debug('beta: %e, gamma: %e', beta, gamma)

    @property
    def energy(self):
        """
        Returns
        -------
        energy : float
            In units of [eV].
        """
        return self._energy

    @property
    def length(self):
        """
        Get the bunch length in the lab frame.

        Returns
        -------
        length : float
            Bunch length in the lab frame in units of [m].
        """
        return self._bunch_shape.length / self._gamma

    @property
    def longitudinal_offset(self):
        """
        Returns
        -------
        longitudinal_offset : float
            The longitudinal offset of the bunch center to the chamber center in units of [s].
        """
        return self._longitudinal_offset

    @longitudinal_offset.setter
    def longitudinal_offset(self, value):
        """
        Parameters
        ----------
        value : float
            The longitudinal offset of the bunch center to the chamber center in units of [s].
        """
        self._longitudinal_offset = value

    @property
    def particle_type(self):
        """
        Returns
        -------
        particle_type : :class:`ParticleType`
        """
        return self._particle_type

    def as_json(self):
        attributes = super().as_json()
        attributes.update({
            'bunch shape': self._bunch_shape.as_json(),
            'bunch electric field model': self._bunch_electric_field_model.as_json(),
            'population in number of charges': '%e' % self._population_in_number_of_charges,
            'total charge': '%e' % self._total_charge,
            'longitudinal offset to chamber': '%e' % self._longitudinal_offset,
            'transverse offset to chamber': self._transverse_offset.tolist(),
        })
        return attributes

    # noinspection PyUnusedLocal
    def charge_density_at(self, position_four_vectors, progress):
        """
        Request the bunch's charge density at the specified positions and at the
        specified simulation progress.

        Parameters
        ----------
        position_four_vectors : :class:`~np.ndarray`, shape (4, N)
            Positions in the lab frame, in units of [m].
        progress : :class:Progress`

        Returns
        -------
        charge_density : :class:`~np.ndarray`, shape (N,)
            The charge density at the specified positions in the lab frame, in units of [C/m^3].
        """
        return self._gamma * self._total_charge * (
            self._bunch_shape.normalized_density_at(
                self.compute_positions_in_bunch_frame(position_four_vectors)
            )
        )

    # noinspection PyUnusedLocal
    def linear_charge_density_at(self, position_four_vectors, progress):
        """
        Request the bunch's linear charge density at the specified positions and at the
        specified simulation progress.

        Parameters
        ----------
        position_four_vectors : :class:`~np.ndarray`, shape (4, N)
            Positions in the lab frame, in units of [m]. The x- and y-positions are ignored.
        progress : :class:Progress`

        Returns
        -------
        linear_charge_density : :class:`~np.ndarray`, shape (N,)
            The linear charge density at the specified positions in the lab frame,
            in units of [C/m].
        """
        return self._gamma * self._total_charge * (
            self._bunch_shape.normalized_linear_density_at(
                self.compute_positions_in_bunch_frame(position_four_vectors)[2]
            )
        )

    def longitudinal_position(self, progress):
        """
        Get the current longitudinal position of this bunch.
        
        Parameters
        ----------
        progress : :class:`Progress`
        
        Returns
        -------
        float
        """
        return (self._longitudinal_offset + progress.time) * self._beta * constants.speed_of_light

    def electric_field_at(self, position_four_vectors, progress):
        """
        Request the electric field vectors at the specified positions and at the
        specified simulation progress.

        Parameters
        ----------
        position_four_vectors : :class:`~np.ndarray`, shape (4, N)
        progress : :class:Progress`

        Returns
        -------
        electric_field_vectors : :class:`~np.ndarray`, shape (3, N)

        See Also
        --------
        :method:`EMFieldsCollector.electric_field_at` : For arguments and return values.
        """
        return self.electric_and_magnetic_field_at(position_four_vectors, progress)[0]

    def magnetic_field_at(self, position_four_vectors, progress):
        """
        Request the magnetic field vectors at the specified positions and at the
        specified simulation progress.

        Parameters
        ----------
        position_four_vectors : :class:`~np.ndarray`, shape (4, N)
        progress : :class:Progress`

        Returns
        -------
        magnetic_field_vectors : :class:`~np.ndarray`, shape (3, N)

        See Also
        --------
        :method:`EMFieldsCollector.electric_field_at` : For arguments and return values.
        """
        return self.electric_and_magnetic_field_at(position_four_vectors, progress)[1]

    # noinspection PyUnusedLocal
    def electric_and_magnetic_field_at(self, position_four_vectors, progress):
        """
        Request the electric and magnetic field vectors at the specified positions and at the
        specified simulation progress.

        Parameters
        ----------
        position_four_vectors : :class:`~np.ndarray`, shape (4, N)
        progress : :class:`Progress`

        Returns
        -------
        em_field_vectors : tuple
            The first element are the electric field vectors and the second element are the
            magnetic field vectors.

        See Also
        --------
        :method:`EMFieldsCollector.electric_field_at` : For arguments and return values.
        """
        return self._lorentz_boost_electric_field.apply(
            self._population_in_number_of_charges
            * self._bunch_electric_field_model.eval(
                self.compute_positions_in_bunch_frame(position_four_vectors)
            )
        )

    def compute_positions_in_bunch_frame(self, position_four_vectors):
        """
        Convert the given positions in the lab frame to positions in the bunch frame.

        Parameters
        ----------
        position_four_vectors : :class:`~np.ndarray`, shape (4, N)

        Returns
        -------
        positions : :class:`~np.ndarray`, shape (3, N)
            The corresponding spatial positions in the lab frame,
            given in units of [m].
        """
        # [!] NOTE: If the time-shift gets incorporated into the Lorentz boost then the Lorentz
        #           boost needs to be updated whenever the longitudinal offset is adjusted!
        # The time shift is required because the `_lorentz_boost` assumes that both coordinate systems are synchronized,
        # i.e. their origins coincide (z = z' = 0) at time zero (t = t' = 0).
        # TODO: [Performance] Don't make a copy here but incorporate the time update into
        # the Lorentz transformation instead.
        # Can't modify the original because of for multi-bunch trains this will also offset
        # positions which are considered by different bunches!
        position_four_vectors = position_four_vectors.copy()
        position_four_vectors[0] += self._longitudinal_offset * constants.speed_of_light
        positions_in_bunch_frame = self._lorentz_boost.apply(position_four_vectors)[1:]
        positions_in_bunch_frame[:2] += self._transverse_offset[:, np.newaxis]
        return positions_in_bunch_frame

    def generate_positions_in_transverse_plane(self, progress, count, z):
        """
        Generate transverse positions in the specified plane according to the Bunch shape's
        particle density.

        Parameters
        ----------
        progress : :class:`Progress`
            The current simulation progress.
        count : int
            Number of positions to be generated.
        z : float
            Longitudinal positions in the lab frame,
            given in units of [m].

        Returns
        -------
        positions : :class:`~np.ndarray`, shape (3, `count`)
            Positions are given in the lab frame in units of [m].
        """
        z_bunch_frame = self.compute_positions_in_bunch_frame(
            np.array(
                [progress.time * constants.speed_of_light, 0., 0., z], dtype=float
            ).reshape(4, 1)
        )[2]
        transverse_positions = \
            self._bunch_shape.generate_positions_in_transverse_plane(count, z_bunch_frame)
        positions = np.empty(shape=(3, count), dtype=float)
        positions[:2] = transverse_positions + self._transverse_offset[:, None]
        positions[2] = z
        return positions
