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

import injector

from virtual_ipm.components import Component
import virtual_ipm.di as di
from virtual_ipm.timings import measure_cpu_time


class EMFieldsCollector(Component):
    """
    This component provides the total electric and magnetic field which is the sum of all
    relevant component of the simulation (beam fields and guiding fields).
    """

    @injector.inject(
        beam_fields=di.components.beams,
        guiding_fields=di.components.guiding_fields
    )
    def __init__(self, beam_fields, guiding_fields):
        """
        Parameters
        ----------
        beam_fields : :class:`BeamsWrapper`
        guiding_fields : :class:`GuidingFieldManager`
        """
        super().__init__()
        self._field_managers = (beam_fields, guiding_fields)
        self._guiding_fields = guiding_fields

    @measure_cpu_time
    def prepare(self):
        """
        Prepare all EM-field managers of the simulation.
        """
        super().prepare()
        # Don't prepare the beam_fields manager because the beams are already prepared from the
        # simulation instance itself.
        self._guiding_fields.prepare()

    @measure_cpu_time
    def electric_field_at(self, position_four_vectors, progress):
        """
        Retrieve the electric field vectors at the specified positions and at the
        current simulation step.

        Parameters
        ----------
        position_four_vectors : :class:`~numpy.ndarray`, shape (4, N)
            The positions and time components of particles as column-four-vectors. Therefore
            the shape of the given array is `(4, N)` for `N` particles and
            ``position_four_vector[0]`` returns the time component for each particle (multiplied
            with the speed of light); positions are given in units of [m] in the lab frame.
        progress : :class:`Progress`

        Returns
        -------
        electric_field_vectors : :class:`numpy.ndarray`
            The electric field vectors evaluated at the given positions; the shape of
            the returned array is `(3, N)` for `N` particles and ``electric_field[0]`` returns
            the field vectors' x-component for all particles; the electric field is given
            in units of [V/m] in the lab frame.
        """
        return sum(map(
            lambda manager: manager.electric_field_at(position_four_vectors, progress),
            self._field_managers
        ))

    @measure_cpu_time
    def magnetic_field_at(self, position_four_vectors, progress):
        """
        Retrieve the magnetic field vectors at the specified positions and at the
        current simulation step.

        Parameters
        ----------
        position_four_vectors : :class:`~numpy.ndarray`, shape (4, N)
            The positions and time components of particles as column-four-vectors. Therefore
            the shape of the given array is `(4, N)` for `N` particles and
            ``position_four_vector[0]`` returns the time component for each particle (multiplied
            with the speed of light); positions are given in units of [m] in the lab frame.
        progress : :class:`Progress`

        Returns
        -------
        magnetic_field_vectors : :class:`~numpy.ndarray`
            The magnetic field vectors evaluated at the given positions; the shape of
            the returned array is `(3, N)` for `N` particles and ``magnetic_field[0]`` returns
            the field vectors' x-component for all particles; the magnetic field is given
            in units of [T] in the lab frame.
        """
        return sum(map(
            lambda manager: manager.magnetic_field_at(position_four_vectors, progress),
            self._field_managers
        ))
