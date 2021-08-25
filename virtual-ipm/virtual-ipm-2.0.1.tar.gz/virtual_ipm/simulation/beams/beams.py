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

from anna.exceptions import InvalidPathError
import injector

from virtual_ipm.components import Component
import virtual_ipm.di as di
from virtual_ipm.simulation.errors import ConfigurationError
from virtual_ipm.timings import measure_cpu_time

from .factory import BeamFactory


class BeamsWrapper(Component):
    """Wrapper for all beams that take part in the simulation."""

    PATH_TO_BEAMS = 'Beams'

    @injector.inject(
        configuration=di.components.configuration,
        device=di.components.device
    )
    def __init__(self, configuration, device):
        super().__init__()
        try:
            beam_configs = configuration.get_sub_configurations(self.PATH_TO_BEAMS)
        except InvalidPathError:
            self._beams = []
        else:
            beam_factory = BeamFactory(device)
            self._beams = [beam_factory.create(config) for config in beam_configs]

    def __getitem__(self, item):
        try:
            return self._beams[item]
        except IndexError:
            raise ConfigurationError(
                'Attempt to retrieve beam #{0} however only {1} beams were defined'.format(
                    item, len(self._beams)
                )
            ) from None

    def __iter__(self):
        return iter(self._beams)

    def __len__(self):
        return len(self._beams)

    def as_json(self):
        return dict(
            super().as_json(),
            beams=list(map(lambda b: b.as_json(), self._beams))
        )

    @measure_cpu_time
    def prepare(self):
        """
        Prepare the beams that take part in the simulation.
        """
        super().prepare()
        for beam in self._beams:
            beam.prepare()

    @measure_cpu_time
    def electric_field_at(self, position_four_vectors, progress):
        """
        Request the electric field vectors at the specified positions and at the
        specified simulation progress.

        Parameters
        ----------
        position_four_vectors : :class:`~numpy.ndarray`, shape (4, N)
            For more information see :method:`EMFieldsCollector.electric_field_at`.
        progress : Progress

        Returns
        -------
        electric_field_vectors : :class:`~numpy.ndarray`, shape (3, N)
            For more information see :method:`EMFieldsCollector.electric_field_at`.
        """
        return sum(map(
            lambda beam: beam.electric_field_at(position_four_vectors, progress),
            self._beams
        ))

    @measure_cpu_time
    def magnetic_field_at(self, position_four_vectors, progress):
        """
        Request the magnetic field vectors at the specified positions and at the
        specified simulation progress.

        Parameters
        ----------
        position_four_vectors : :class:`~numpy.ndarray`, shape (4, N)
            For more information see :method:`EMFieldsCollector.magnetic_field_at`.
        progress : Progress

        Returns
        -------
        magnetic_field_vectors : :class:`~numpy.ndarray`, shape (3, N)
            For more information see :method:`EMFieldsCollector.magnetic_field_at`.
        """
        return sum(map(
            lambda beam: beam.magnetic_field_at(position_four_vectors, progress),
            self._beams
        ))
