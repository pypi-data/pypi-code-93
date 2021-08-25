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
from rx.subjects import Subject

from virtual_ipm.components import Component
import virtual_ipm.control.commands as commands
import virtual_ipm.di as di
from virtual_ipm.timings import measure_cpu_time


class IPMSimulation(Component):
    """
    Use this class to run an IPM simulation. Before running the simulation via
    :method:`~IPMSimulation.run` it has to be prepared via :method:`~IPMSimulation.prepare`.
    """

    @injector.inject(
        beams=di.components.beams,
        device=di.components.device,
        particle_generation=di.components.particle_generation,
        particle_tracking=di.components.particle_tracking,
        output=di.components.output,
        setup=di.components.setup
    )
    def __init__(self, beams, device, particle_generation, particle_tracking, output, setup):
        """
        Parameters
        ----------
        beams : :class:`BeamsWrapper`
        device : :class:`DeviceManager`
        particle_generation : :class:`ParticleGenerationManager`
        particle_tracking : :class:`ParticleTrackingManager`
        output : :class:`OutputRecorder`
        setup : :class:`Setup`
        """
        super().__init__()
        self.log.debug('Setup: {}'.format(setup))
        self._beams = beams
        self._device = device
        self._particle_generation = particle_generation
        self._particle_tracking = particle_tracking
        self._output = output
        self._setup = setup
        self._cycle = SimulationCycle(
            self._beams,
            self._device,
            self._particle_generation,
            self._particle_tracking,
            self._output,
            self._setup
        )
        if setup.only_generate_particles:
            self.log.info('Using advanced option "OnlyGenerateParticles" (no tracking will be performed)')
            self._execute = Iteration.execute_only_particle_generation
        else:
            self._execute = Iteration.execute
        self._run_flag = True

        def stop_on_next_iteration(cmd):
            if cmd == commands.STOP:
                self._run_flag = False

        commands.feed.subscribe(stop_on_next_iteration)

        self._has_been_prepared = False

    @measure_cpu_time
    def prepare(self):
        """
        Prepare all components of the simulation.
        """
        self.log.info('Preparing simulation')
        self._beams.prepare()
        self._device.prepare()
        self._particle_generation.prepare()
        self._particle_tracking.prepare()
        self._output.prepare()
        self._has_been_prepared = True

    @measure_cpu_time
    def run(self):
        """
        Start the simulation cycle.
        """
        if not self._has_been_prepared:
            raise RuntimeError(
                'The simulation first needs to be prepared by calling %s.prepare'
                % self.__class__.__name__
            )
        with self._output as output_recorder:
            try:
                for iteration, progress in self._cycle:
                    if self._run_flag:
                        self._execute(iteration)
                        output_recorder.record(progress)
                    else:
                        self._cycle.abort()
            except StopIteration:
                pass

    @property
    def progress(self):
        """
        Proxy for :method:`SimulationCycle.progress`.

        Returns
        -------
        progress : :class:`rx.subjects.Subject`
        """
        return self._cycle.progress


class SimulationCycle(Component):
    # noinspection PyUnresolvedReferences
    """
    Use this class for running a simulation cycle. The single iterations are obtained by
    iterating over the SimulationCycle instance.

    Examples
    --------
    >>> for iteration in simulation_cycle:
    ...     iteration.execute()
    """
    def __init__(self, beams, device, particle_generation, particle_tracking, output, setup):
        """
        Parameters
        ----------
        beams : :class:`BeamsWrapper`
        device : :class:`DeviceManager`
        particle_generation : :class:`ParticleGenerationManager`
        particle_tracking : :class:`ParticleTrackingManager`
        output : :class:`OutputRecorder`
        setup : :class:`Setup`
        """
        super().__init__()
        self._beams = beams
        self._device = device
        self._particle_generation = particle_generation
        self._particle_tracking = particle_tracking
        self._output = output
        self._setup = setup
        self._progress = Subject()

    def __iter__(self):
        """
        Yield iterations until the simulation cycle is completed.

        Returns
        -------
        iterator[:class:`Iteration`]
            The single iterations which form the cycle.
        """
        self.log.info('Start simulation cycle')
        for step in range(self._setup.number_of_time_steps):
            progress = Progress(step, self._setup.number_of_time_steps, self._setup.time_delta)
            yield (
                Iteration(
                    self._device, self._particle_generation, self._particle_tracking, progress
                ),
                progress
            )
            self._progress.on_next(progress)
            self.log.info('Completed step %d', step)
        self._finalize()
        self.log.info('Completed simulation cycle')

    def abort(self):
        """
        Abort the simulation cycle by raising a ``StopIteration`` exception.

        Raises
        ------
        StopIteration
        """
        self.log.info('Simulation cycle stopped')
        raise StopIteration

    @property
    def progress(self):
        """
        Stream which provides updates about the simulation progress in form of
        :class:`Progress` instances.

        Returns
        -------
        progress : :class:`rx.subjects.Subject`
        """
        return self._progress

    # noinspection PyMethodMayBeStatic
    def _finalize(self, ):
        """
        Finalize the simulation cycle by performing tasks after the actual cycle has completed.
        """
        # Could scan particles one more time to make sure they are detected/invalidated properly
        # if they hit the detector / boundary during the last time step.
        pass


class Iteration:
    """
    An iteration during a simulation cycle. The iteration can be performed by calling
    :method:`~Iteration.execute`. An iteration involves the following steps:

      * Generate particles.
      * Scan particles (check if they hit the boundary / reached the detector).
      * Propagate (track) particles.

    The reason that scanning is performed before tracking is that if particles are created at
    invalid positions they are removed from the simulation before they are tracked further.
    """
    def __init__(self, device, particle_generation, particle_tracking, progress):
        """
        Parameters
        ----------
        device : :class:`DeviceManager`
        particle_generation : :class:`ParticleGenerationManager`
        particle_tracking : :class:`ParticleTrackingManager`
        progress : :class:`Progress`
        """
        super().__init__()
        self._device = device
        self._particle_generation = particle_generation
        self._particle_tracking = particle_tracking
        self._progress = progress

    def execute(self):
        """
        Perform the steps during this iteration.
        """
        self._particle_generation.generate_particles(self._progress)
        self._device.scan_particles(self._progress)
        self._particle_tracking.propagate_particles(self._progress)

    def execute_only_particle_generation(self):
        """
        Only perform particle generation during this iteration.
        """
        self._particle_generation.generate_particles(self._progress)


class Progress:
    # noinspection PyUnresolvedReferences
    """
    Represents the progress during a simulation cycle.
        
    Attributes
    ----------
    max_steps
    step
    time
    """
    def __init__(self, step, max_steps, time_delta):
        """
        Parameters
        ----------
        step : int
            The current simulation step.
        max_steps : int
            The number of simulation steps that need to be performed in order to complete the cycle.
        time_delta : float
            The time which elapses between two simulation steps, in units of [s].
        """
        super().__init__()
        self._step = step
        self._max_steps = max_steps
        self._time_delta = time_delta

    def __iter__(self):
        """
        Returns
        -------
        iterator
            First element is the simulation step, second element is the number of steps for
            the whole cycle.
        """
        return iter((self._step, self._max_steps))

    def __repr__(self):
        return '{0}({1}, {2}, {3}'.format(
            self.__class__.__name__,
            self._step,
            self._max_steps,
            self._time_delta
        )

    @property
    def max_steps(self):
        """
        Returns
        -------
        max_steps : int
            The number of simulation steps that need to be performed in order to complete
            the cycle.
        """
        return self._max_steps

    @property
    def step(self):
        """
        Returns
        -------
        step : int
            The simulation step corresponding to this progress.
        """
        return self._step

    @property
    def time(self):
        """
        Returns
        -------
        time : float
            The simulation time corresponding to this progress, in units of [s].
        """
        return self._step * self._time_delta
