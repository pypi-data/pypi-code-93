"""This module contains the :class:`MosaikEnvironment`, which
allows to run mosaik co-simulations with palaestrAI.

"""
import threading
from collections import Callable

from palaestrai.environment.environment import Environment
from palaestrai.util.dynaloader import load_with_params

from palaestrai_mosaik import LOG
from palaestrai_mosaik.environment import MosaikWorld
from palaestrai_mosaik.simulator import ShutdownError


class MosaikEnvironment(Environment):
    """The mosaik environment for palaestrAI.

    This class implements the abstract class
    :class:`palaestrai.environment.Environment` and allows the
    interaction between ARL agents and a mosaik co-simulation.

    Parameters
    ----------
    connection: str
        The connection to the broker, required by the *Environment*
        class.
    uid: str
        The uid of this environment, required by the *Environment*
        class.
    seed: int
        A random seed provided by the experiment.
    params: dict
        A *dict* containing information about the mosaik world that
        should be created. This should look, e.g, like::

            params = {
                # Full import path to a module or class
                "module": "midas.adapter.arl:Descriptor",
                # A function of *module* that returns descriptions
                # of sensors and actuators
                "description_func": "describe",
                # A function of *module* that returns a mosaik world
                # object
                "instance_func": "get_world",
                # Step size for the ARL synchronization
                "step_size": 900,
                # Additional params passed to *description_func* and
                # *instance_func*
                "params": {},
            }

    Attributes
    ----------
    mworld: :class:`.MosaikWorld`
        Creates and holds the mosaik world object.

    """

    def __init__(
            self, uid: str, broker_uri: str, seed: int, **params
    ):
        super().__init__(uid, broker_uri, seed, **params)

        self.mworld = None
        self._env_task = None
        self._event_communicated = None
        self._event_stepped = None
        self._event_shutdown = None

        self._ctr_com = -1
        self._ctr_mos = -1
        self._shutdown = False
        self._mosaik_finished = False

        self.reward = load_with_params(params["params"]["reward"]["name"], params["params"]["reward"]["params"])

    def start_environment(self):
        self.mworld = None
        self._env_task = None
        self._event_communicated = threading.Event()
        self._event_stepped = threading.Event()
        self._event_shutdown = threading.Event()

        self._ctr_com = -1
        self._ctr_mos = -1
        self._shutdown = False
        self._mosaik_finished = False

        LOG.debug(
            "EnvironmentCOM %s(id=0x%x, uid=%s) is creating world object "
            "...",
            self.__class__,
            id(self),
            self.uid,
        )
        self.mworld = MosaikWorld(self)
        LOG.debug(
            "EnvironmentCOM %s(id=0x%x, uid=%s) is setting up simulators, "
            "connecting entities ...",
            self.__class__,
            id(self),
            self.uid,
        )
        self.mworld.setup(self._params)
        LOG.debug(
            "EnvironmentCOM %s(id=0x%x, uid=%s) is starting mosaik "
            "simulation process ... ",
            self.__class__,
            id(self),
            self.uid,
        )
        self._env_task = threading.Thread(target=self.start)
        self._env_task.start()
        LOG.info(
            "EnvironmentCOM %s(id=0x%x, uid=%s) finished setup. "
            "Co-simulation is now running.",
            self.__class__,
            id(self),
            self.uid,
        )
        return self.mifs.sensors, self.mifs.actuators

    def update(self, actuators):
        """Update the environment with new actuator values.

        On each call,  *actuators* contains new values, which will be
        injected into the mosaik data graph so that simulators can
        fetch these values without even noticing.

        This method implements the communication part of the
        synchronization between worker process and the mosaik process.

        Parameters
        ----------
        actuators : list[ActuatorInformation]
            A *list* of actuators with new values provided by the
            agents.

        Returns
        -------
        tuple
            A *tuple* containing a *list*, a *float*, and a *bool*
            The list contains sensors with updated values, the float
            represents a reward defining the current state of the
            environment, and the bool is False if the environment is
            still running and True otherwise.

        """
        LOG.debug(
            "EnvironmentCOM %s(id=0x%x, uid=%s) New update request.",
            self.__class__,
            id(self),
            self.uid,
        )

        if len(actuators) > 0:
            LOG.debug(
                "EnvironmentCOM %s(id=0x%x, uid=%s) Now updating "
                "actuators ...",
                self.__class__,
                id(self),
                self.uid,
            )
            self.mifs.update_actuators(actuators)
        else:
            LOG.debug(
                "EnvironmentCOM %s(id=0x%x, uid=%s) actuator list "
                "is empty!",
                self.__class__,
                id(self),
                self.uid,
            )

        self._ctr_com += 1
        if self._mosaik_finished:
            LOG.debug(
                "EnvironmentCOM %s(id=0x%x, uid=%s) noticed that "
                "mosaik finished.",
                self.__class__,
                id(self),
                self.uid,
            )
            return list(), True

        while self._ctr_mos <= self._ctr_com:
            if self._mosaik_finished:
                LOG.debug(
                    "EnvironmentCOM %s(id=0x%x, uid=%s) noticed that "
                    "mosaik finished.",
                    self.__class__,
                    id(self),
                    self.uid,
                )
                return list(), True
            self._event_communicated.set()
            self._event_stepped.wait()
            self._event_stepped.clear()

        LOG.debug(
            "EnvironmentCOM %s(id=0x%x, uid=%s): Now mosaik should be "
            "waiting. Starting communication ...",
            self.__class__,
            id(self),
            self.uid,
        )

        sensors = self.mifs.get_sensor_readings()

        LOG.debug(
            "EnvironmentCOM %s(id=0x%x, uid=%s) received sensor "
            "readings %s from mosaik",
            self.__class__,
            id(self),
            self.uid,
            sensors,
        )

        return sensors, self.reward(sensors), False

    def sync(self, time):
        """Allow synchronization with the message worker.

        This method is called each time the :class:`.ARLSyncSimulator`
        steps. Updates the values in the sensor objects directly from
        the mosaik data graph.

        The actuator values will not be set here, since each simulator
        fetches its input data directly and independently from mosaik.

        This method implements the mosaik part of the synchronization
        between worker and mosaik process.

        Parameters
        ----------
        time : int
            The current simulation time (current step) is required to
            retrieve the correct data from the mosaik world.

        """
        LOG.debug(
            "EnvironmentMOS %s(id=0x%x, uid=%s) updated.",
            self.__class__,
            id(self),
            self.uid,
        )
        self.mifs.trigger_sensors(self.mworld.world, time)

        self._ctr_mos += 1

        if self._shutdown:
            raise ShutdownError
        LOG.debug(
            "EnvironmentMOS %s(id=0x%x, uid=%s) signalling COM ...",
            self.__class__,
            id(self),
            self.uid,
        )
        while self._ctr_mos > self._ctr_com:
            self._event_stepped.set()
            if self._shutdown:
                raise ShutdownError
            self._event_communicated.wait()
            self._event_communicated.clear()

        LOG.debug(
            "EnvironmentMOS %s(id=0x%x, uid=%s): now com should be "
            "waiting. Start next step ...",
            self.__class__,
            id(self),
            self.uid,
        )

    def shutdown(self, reset=False):
        """Try to shutdown the environment.

        Returns
        -------
        bool
            True if the environment was shut down, False otherwise.

        """
        LOG.info(
            "EnvironmentCOM %s(id=0x%x, uid=%s) attempting to stop "
            "the co-simulation ...",
            self.__class__,
            id(self),
            self.uid,
        )
        self._shutdown = True
        self._event_communicated.set()

        self._env_task.join()

        self._event_shutdown.wait()
        LOG.debug(
            "EnvironmentCOM %s(id=0x%x, uid=%s) The counter for mosaik "
            "should be -1 if the shutdown was "
            "sucessful. Counter value is : %d",
            self.__class__,
            id(self),
            self.uid,
            self._ctr_mos,
        )
        self.is_terminal = not reset
        return self._mosaik_finished

    def start(self):
        """Start the simulation process.

        As soon as the mosaik simulation is finished (or interrupted),
        events are set to notify the worker that the simulation is
        finished.

        """
        self.mworld.start()
        self._ctr_mos = -1
        self._mosaik_finished = True
        self._event_shutdown.set()
        self._event_stepped.set()

    @property
    def mifs(self):
        """Return the mosaik interface component.

        Holds the sensors and actuators and handles the exchange of
        data between the communication worker and the mosaik simpy
        process.

        Returns
        -------
        :class:`.MosaikInterfaceComponent`

        """
        return self.mworld.mifs
