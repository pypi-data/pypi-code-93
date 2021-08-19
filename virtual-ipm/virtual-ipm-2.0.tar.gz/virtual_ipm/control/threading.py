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

import threading
import sys

import injector
from rx.subjects import Subject

import virtual_ipm.di as di
from virtual_ipm.di.bindings import create_binding_for_component, create_bindings


class DependencyWrapper:
    """
    Auxiliary class for pulling in components from the DI framework which are required for
    running the simulation:

      * :class:`OutputRecorder`
      * :class:`ParticleSupervisor`
      * :class:`Setup`
      * :class:`Simulation`
    """

    @injector.inject(
        output=di.components.output,
        particle_supervisor=di.components.particle_supervisor,
        setup=di.components.setup,
        simulation=di.components.simulation
    )
    def __init__(self, output, particle_supervisor, setup, simulation):
        self.output = output
        self.particle_supervisor = particle_supervisor
        self.setup = setup
        self.simulation = simulation

    @classmethod
    def create_binding(cls):
        """
        Create a binding for this component within the DI framework.

        Returns
        -------
        binding : tuple
            ``binding[0]`` is the binding key, ``binding[1]`` is the binding module.
        """
        binding_key = injector.BindingKey(cls.__name__)
        return binding_key, create_binding_for_component(cls, binding_key)


class SimulationThread(threading.Thread):
    """
    Allows to run the simulation in a separate thread and provides proxy methods for connecting to
    components of the simulation.
    Before running the simulation you must call :method:`~SimulationThread.setup` as well as
    :method:`~SimulationThread.prepare`.
    To run the simulation in a separate thread use :method:`~SimulationThread.start`,
    to run it in the same thread use :method:`~SimulationThread.run`.
    """

    def __init__(self):
        super().__init__()
        self._errors = Subject()
        self._particle_supervisor_status_updates = Subject()
        self._progress_updates = Subject()
        self._position_updates = Subject()
        self._simulation = None
        self._config = None
        self._is_prepared = False

    @property
    def errors(self):
        """
        The simulation's error stream. All exceptions will be published on this stream. The
        published values correspond to the return values of ``sys.exc_info`` at the moment the
        exception was caught: ``(exc_type, exc_value, exc_traceback)``.
        
        Returns
        -------
        errors : :class:`rx.subjects.Subject`
        """
        return self._errors

    @property
    def status_updates(self):
        """
        Proxy for :method:`ParticleSupervisor.status_updates`.

        Returns
        -------
        status_updates : :class:`rx.subjects.Subject`
        """
        return self._particle_supervisor_status_updates

    @property
    def progress(self):
        """
        Proxy for :method:`Simulation.progress`.

        Returns
        -------
        status_updates : :class:`rx.subjects.Subject`
        """
        return self._progress_updates

    @property
    def position_updates(self):
        """
        Proxy for :method:`PublishingRecorder.position_updates`.

        Returns
        -------
        position_updates : :class:`rx.subjects.Subject`
        """
        return self._position_updates

    def setup(self, config):
        """
        Fetch the simulation instance from the DI framework and subscribe the proxies to
        the corresponding subjects.

        Parameters
        ----------
        config : :class:`ConfigurationAdaptor` derived class
        """
        self._config = config
        binding_key, binding_module = DependencyWrapper.create_binding()
        injector_container = injector.Injector(create_bindings(self._config) + [binding_module])
        dependency_wrapper = injector_container.get(binding_key)

        dependency_wrapper.particle_supervisor.status_updates.subscribe(
            self._particle_supervisor_status_updates.on_next)
        dependency_wrapper.simulation.progress.subscribe(self._progress_updates.on_next)
        if hasattr(dependency_wrapper.output, str('position_updates')):
            dependency_wrapper.output.position_updates.subscribe(self._position_updates)

        self._simulation = dependency_wrapper.simulation

    def prepare(self):
        """Prepare the underlying simulation. This is required before the simulation thread can be started."""
        if self._simulation is None:
            raise RuntimeError(f'You need to call {self.__class__.__name__}.setup first')
        self._simulation.prepare()
        self._is_prepared = True

    def run(self):
        """
        Start the simulation. Invoking this method directly will run the simulation
        in the same thread. To run the simulation in a separate thread use
        :method:`~SimulationThread.start`.

        .. note::
        You need to call :method:`~SimulationThread.setup` before invoking this method.

        Raises
        ------
        RuntimeError
            If :method:`~SimulationThread.setup` has not been called prior to this method.
        """
        if not self._is_prepared:
            raise RuntimeError(f'You need to call {self.__class__.__name__}.prepare first')
        try:
            self._simulation.run()
        except Exception:
            self._errors.on_next(sys.exc_info())
            raise
