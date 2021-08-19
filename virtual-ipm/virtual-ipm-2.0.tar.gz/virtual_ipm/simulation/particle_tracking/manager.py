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
import scipy.constants as constants

import virtual_ipm.di as di
from virtual_ipm.components import Manager
from virtual_ipm.timings import measure_cpu_time


class ParticleTrackingManager(Manager):
    """
    This component provides functionality for propagating particles throughout the simulation.
    """

    @injector.inject(
        em_fields=di.components.em_fields,
        model=di.models.particle_tracking,
        particle_supervisor=di.components.particle_supervisor
    )
    def __init__(self, em_fields, model, particle_supervisor):
        super().__init__()
        self._em_fields = em_fields
        self._model = model
        self._particle_supervisor = particle_supervisor

    def as_json(self):
        return dict(
            super().as_json(),
            model=self._model.as_json()
        )

    @measure_cpu_time
    def prepare(self):
        """
        Prepare the particle tracking model and the electromagnetic fields components
        which are used for tracking.
        """
        super().prepare()
        self._em_fields.prepare()
        self._model.prepare()

    @measure_cpu_time
    def initialize(self, particles, progress):
        """
        Initialize the given particles. This achieved through invoking the model's
        :method:`~ParticleTrackingModel.initialize` method as well as setting the status
        of particles to "tracked".

        Parameters
        ----------
        particles : :class:`ParticleIndexView`
        progress : :class:`Progress`
        """
        self.log.debug('[%s] Initializing %d particles', progress, len(particles))
        self._model.initialize(particles, progress)
        self._particle_supervisor.track(particles, progress)

    @measure_cpu_time
    def propagate_particles(self, progress):
        """
        Propagate all particles that are currently being tracked. Before this initialize all
        particles that are queued for tracking and set their status to "tracked".
        Propagating is achieved by invoking the model's :method:`~ParticleTrackingModel.propagate`
        method. Before particles are propagated their time-component is also update to match
        the given simulation progress.

        Parameters
        ----------
        progress : :class:`Progress`
        """
        # Could also subscribe to ParticleSupervisor.status_updates and initialize particles
        # whenever they are set QUEUED (or omit QUEUED and set directly TRACKED).
        queued_particles = self._particle_supervisor.queued_particles
        if queued_particles:
            self.initialize(queued_particles, progress)
        tracked_particles = self._particle_supervisor.tracked_particles
        if tracked_particles:
            self.log.debug('[%s] Tracking %d particles', progress, len(tracked_particles))
            # Adjust (simulation) time for tracked particles.
            tracked_particles.time = constants.speed_of_light * progress.time
            self._model.propagate(tracked_particles, progress)
