"""This module contains the :class:`.MosaikWorld` class, which is home
of the mosaik world object and cares for setup and shutdown of the
world.

"""
from mosaik.exceptions import ScenarioError
from mosaik.scenario import Entity
from palaestrai_mosaik.config import AGENT_SID
from palaestrai_mosaik.environment import LOG, MosaikInterfaceComponent, loader
from palaestrai_mosaik.mosaikpatch.scenario import modify_world
from palaestrai_mosaik.simulator import ShutdownError


class MosaikWorld:
    """The home for mosaik worlds.

    This class creates sensor and actuator descriptions and the world
    objectby calling the :func:`description_func` and
    :func:`instance_func` defined in the params dictionary.

    Furthermore, the :class:`.ARLSyncSimulator` is injected into the
    world object and integrated into the mosaik dependency graph.

    Parameters
    ----------
    env : :class:`.MosaikEnvironment`
        A reference to the environment creating this object.

    Attributes
    ----------
    env : :class:`.MosaikEnvironment`
        Stores the reference to the environment creating this object.
    world : :class:`mosaik.scenario.World`
        The world object created during the setup method.
    end : int
        The number of simulation steps mosaik will simulate.
    mifs : :class:`.MosaikInterfaceComponent`
        Stores all sensors and actuators and manages their data.

    """

    def __init__(self, env):
        self.env = env
        self.world = None
        self.end = None
        self.mifs = None

    def setup(self, params):
        """Setup the mosaik environment.

        A couple of things need to be done to prepare the environment.

        Parameters
        ----------
        params : dict
            A *dict* with information about the mosaik world to be
            created.

        """
        params = params["params"]
        self.end = get_end(params["end"])

        dscr_func, inst_func = loader.load_funcs(params)
        sen_dscr, act_dscr = dscr_func(params["params"])

        self.world = inst_func(params["params"])
        modify_world(self.world)

        self.mifs = MosaikInterfaceComponent(sen_dscr, act_dscr)
        self.mifs.create_sensors()
        self.mifs.create_actuators()

        agent = self.inject_arl(params["step_size"])
        self.connect(agent)

        self.world.trigger_actuators = self.mifs.trigger_actuators

    def inject_arl(self, step_size):
        """Prepare the world for ARL.

        The world object is extended by an instance of the
        :class:`.ARLSyncSimulator` which controls an *ARLAgent* mosaik
        entity.

        Returns
        -------
        :class:`mosaik.scenario.Entity`
            The agent entity object created by mosaik.

        """

        self.world.sim_config[AGENT_SID] = {
            "python": "palaestrai_mosaik.simulator:ARLSyncSimulator"
        }
        arl_sim = self.world.start(
            AGENT_SID, env=self.env, step_size=step_size
        )

        return arl_sim.ARLAgent()

    def connect(self, agent):
        """Establishs mosaik connections from sensor entities.

        The collected data is not used since the data is directly
        gathered from the world object. Instead, this step is required
        to get the simulator in sync with the other simulators. For
        this purpose, it would be enought to connect to a single other
        simulator, but to be sure we connect to every simulator that
        provides sensors.

        This is also on reason, why there will be no actuator
        connections. Furthermore, this would require to make use of
        the :attr:`time_shifted` parameter of the
        :meth:`mosaik.scenario.World.connect` method, which needs to be
        provided with :attr:`initial_data`, which we not have.
        Eventually, the actuator data will be injected directly into
        the world object.

        Notes
        -----
            While the *sid* has kind of standardized naming, this is
            not true for the eid, since it is task of each simulator to
            provide eids. Therefore, this might fail, although the
            sensor description SHOULD have the correct name.

            The *connect* method of the mosaik world currently does
            not use the entity's children. Therefore, passing an empty
            list is not a problem. This may change in future mosaik
            versions.

        Parameters
        ----------
        agent : :class:`mosaik.scenario.Entity`
            The agent entity to be connected with other entities.

        """
        connections = 0

        for key in self.mifs.sensor_map:
            sid, eid, attr = key.split(".")
            sim = self.world.sims[sid]

            model_type = eid
            for model in sim.meta["models"]:
                if model.lower() in eid.lower():
                    model_type = model

            entity = Entity(
                sid=sid,
                eid=eid,
                sim_name=sid.split("-")[0],
                type=model_type,
                children=list(),
                sim=sim,
            )
            try:
                self.world.connect(entity, agent, attr)
                connections += 1
            except ScenarioError as err:
                LOG.debug("Can't find model for eid %s", eid)
                LOG.debug("Caught the following exception: %s", err)
        if connections < 1:
            LOG.error(
                "Could not create any connection to any mosaik simulator. "
                "Please check your configuration and the log file."
            )
        else:
            LOG.debug(
                "Created %d connections to other simulators", connections
            )

    def start(self):
        """Start the mosaik simulation process."""
        LOG.debug("Starting mosaik ...")
        try:
            self.world.run(until=self.end)
            LOG.debug("Mosaik finished.")
        except ShutdownError:
            LOG.info("Successfully killed mosaik.")


def get_end(end):
    """Read the *end* value from the params dict.

    The *end* value is an integer, but sometimes it is provided
    as float, or as str like '15*60'. In the latter case, the
    str is evaluated (i.e., multiplied). In any case, *end* is
    returned as int.

    """
    if isinstance(end, str):
        parts = end.split("*")
        end = 1
        for part in parts:
            end *= float(part)
    return int(end)
