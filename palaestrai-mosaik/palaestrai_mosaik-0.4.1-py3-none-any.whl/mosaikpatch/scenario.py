"""This module contains a patch for mosaik's world object.

Needs to be updated when the mosaik API changes.

Tested with mosaik version 2.6.0.

"""
import types

import networkx
from mosaik import util

from palaestrai_mosaik.mosaikpatch import LOG, scheduler


def modify_world(world):
    """Modify the world object for the use with palaestrAI.

    A new method :meth:`.trigger_actuators` is installed, which is
    called by the :func:`.get_input_data` function of the modified
    :mod:`~.scheduler`. Furthermore, the
    :func:`mosaik.scenario.World.run` method is overwritten by the
    modified :func:`~.run` version below.

    Parameters
    ----------
    world : :class:`mosaik.scenario.World`
        The *world* object to be modified.

    """
    LOG.debug("Installing 'trigger_actuators' method.")
    setattr(world, "trigger_actuators", None)
    LOG.debug("Modifying 'run' method.")
    setattr(world, "run", types.MethodType(run, world))


def run(self, until, rt_factor=None, rt_strict=False, print_progress=True):
    """A modified version of the :func:`mosaik.scenario.World.run`
    method of mosaik's world object.

    This :func:`~.run` method works exactly like the original one
    except that a different scheduler is used. Indeed, it is nearly the
    same code but since a modified scheduler is imported, this specific
    scheduler is called instead.

    Furthermore, the prints are replaced by logging outputs.

    See the mosaik documentation
    https://mosaik.readthedocs.io/en/latest/api_reference/mosaik.scenario.html
    :func:`mosaik.scenario.World.run` for the regular features of this
    method.

    """
    if self.srv_sock is None:
        raise RuntimeError(
            "Simulation has already been run and can only "
            "be run once for a World instance."
        )

    # Check if a simulator is not connected to anything:
    for sid, deg in sorted(list(networkx.degree(self.df_graph))):
        if deg == 0:
            LOG.warning("WARNING: %s has no connections.", sid)

    LOG.debug("Starting simulation.")
    import mosaik._debug as dbg  # always import, enable when requested

    if self._debug:
        dbg.enable()
    try:
        util.sync_process(
            scheduler.run(self, until, rt_factor, rt_strict, print_progress),
            self,
        )
        LOG.debug("Simulation finished successfully.")
    except KeyboardInterrupt:
        LOG.info("Simulation canceled. Terminating ...")
    finally:
        self.shutdown()
        if self._debug:
            dbg.disable()
