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


class DeviceManager(Manager):
    """
    This component provides functionality for checking if particles are to be detected or if
    they reached an invalid situation.
    
    Attributes
    ----------
    x_boundaries : :class:`~numpy.ndarray`, shape (2,)
        In units of [m]. The first item denotes the lower and the second item the upper
        boundary: ``x_boundaries[0] < x_boundaries[1]``.
    y_boundaries : :class:`~numpy.ndarray`, shape (2,)
        In units of [m]. The first item denotes the lower and the second item the upper
        boundary: ``y_boundaries[0] < y_boundaries[1]``.
    z_boundaries : :class:`~numpy.ndarray`, shape (2,)
        In units of [m]. The first item denotes the lower and the second item the upper
        boundary: ``z_boundaries[0] < z_boundaries[1]``.
    """

    @injector.inject(
        device=di.models.device,
        particle_supervisor=di.components.particle_supervisor
    )
    def __init__(self, device, particle_supervisor):
        super().__init__()
        self._device = device
        self._particle_supervisor = particle_supervisor
        self.x_boundaries = self._device.x_boundaries
        self.y_boundaries = self._device.y_boundaries
        self.z_boundaries = self._device.z_boundaries

    def as_json(self):
        return dict(
            super().as_json(),
            model=self._device.as_json()
        )

    @measure_cpu_time
    def prepare(self):
        """
        Prepare the device model.
        """
        super().prepare()
        self._device.prepare()

    @measure_cpu_time
    def scan_particles(self, progress):
        """
        Scan all particles that are currently being tracked and update their statuses if necessary.
        This is achieved by invoking the model's :method:`DeviceModel.scan_particles` method.

        Parameters
        ----------
        progress : :class:`Progress`
        """
        tracked_particles = self._particle_supervisor.tracked_particles
        if tracked_particles:
            self._device.scan_particles(tracked_particles, progress)

    @property
    def x_min(self):
        """
        Retrieve the lower boundary in x-direction.

        Returns
        -------
        x_min : float
            In units of [m].
        """
        return self.x_boundaries[0]

    @property
    def x_max(self):
        """
        Retrieve the upper boundary in x-direction.

        Returns
        -------
        x_max : float
            In units of [m].
        """
        return self.x_boundaries[1]

    @property
    def y_min(self):
        """
        Retrieve the lower boundary in y-direction.

        Returns
        -------
        y_min : float
            In units of [m].
        """
        return self.y_boundaries[0]

    @property
    def y_max(self):
        """
        Retrieve the upper boundary in y-direction.

        Returns
        -------
        y_max : float
            In units of [m].
        """
        return self.y_boundaries[1]

    @property
    def z_min(self):
        """
        Retrieve the lower boundary in z-direction.

        Returns
        -------
        z_min : float
            In units of [m].
        """
        return self.z_boundaries[0]

    @property
    def z_max(self):
        """
        Retrieve the upper boundary in z-direction.

        Returns
        -------
        z_max : float
            In units of [m].
        """
        return self.z_boundaries[1]
