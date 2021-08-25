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

from virtual_ipm.components import Manager
import virtual_ipm.di as di
from virtual_ipm.timings import measure_cpu_time


class GuidingFieldsManager(Manager):
    """
    This component provides the guiding fields which are used for the simulation
    """

    @injector.inject(
        electric_field_model=di.models.electric_guiding_field,
        magnetic_field_model=di.models.magnetic_guiding_field
    )
    def __init__(self, electric_field_model, magnetic_field_model):
        """
        Parameters
        ----------
        electric_field_model : ElectricGuidingFieldModel
        magnetic_field_model : MagneticGuidingFieldModel
        """
        super().__init__()
        self._electric_field_model = electric_field_model
        self._magnetic_field_model = magnetic_field_model

    def as_json(self):
        return dict(
            super().as_json(),
            electric_guiding_field=self._electric_field_model.as_json(),
            magnetic_guiding_field=self._magnetic_field_model.as_json(),
        )

    @measure_cpu_time
    def prepare(self):
        """
        Prepare the electric and magnetic guiding field models.
        """
        super().prepare()
        self._electric_field_model.prepare()
        self._magnetic_field_model.prepare()

    @measure_cpu_time
    def electric_field_at(self, position_four_vectors, progress):
        """
        Request the electric field vectors at the specified positions and at the
        specified simulation progress.

        Parameters
        ----------
        position_four_vectors : :class:`~numpy.ndarray`, shape (4, N)
        progress : Progress

        Returns
        -------
        electric_field_vectors : :class:`~numpy.ndarray`, shape (3, N)

        See Also
        --------
        :method:`EMFieldsCollector.electric_field_at` : For arguments and return values.
        """
        return self._electric_field_model.eval(position_four_vectors, progress)

    @measure_cpu_time
    def magnetic_field_at(self, position_four_vectors, progress):
        """
        Request the magnetic field vectors at the specified positions and at the
        specified simulation progress.

        Parameters
        ----------
        position_four_vectors : :class:`~numpy.ndarray`, shape (4, N)
        progress : Progress

        Returns
        -------
        magnetic_field_vectors : :class:`~numpy.ndarray`, shape (3, N)

        See Also
        --------
        :method:`EMFieldsCollector.electric_field_at` : For arguments and return values.
        """
        return self._magnetic_field_model.eval(position_four_vectors, progress)
