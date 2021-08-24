"""This module contains a modified version of the mosaik scheduler.

Since the scheduler is not a class but a collection of functions,
each function of the scheduler needs to be present. For most of them,
calls can be directed to the regular scheduler function. However, as
soon as the mosaik scheduler changes, these changes need to be
reflected here and new functions need a forward call in this module.

The only function with a modification is the
:func:`mosaik.scheduler.get_input_data` function (and there is added
only one line of code). But to make use of this modified function, it
is required to provide copies of :func:`mosaik.scheduler.run` and
:func:`mosaik.scheduler.sim_process`, as well. They should be updated
on a new mosaik version.

See
https://mosaik.readthedocs.io/en/latest/api_reference/mosaik.scheduler.html
for the docs of the original functions.

Tested with mosaik version 2.6.0

"""
from time import perf_counter

import mosaik.scheduler
from mosaik.exceptions import SimulationError
from palaestrai_mosaik.mosaikpatch import LOG


def run(world, until, rt_factor=None, rt_strict=False, print_progress=True):
    """Run the simulation.

    This is an exact copy of the current :func:`mosaik.scheduler.run`
    method.

    """

    if rt_factor is not None and rt_factor <= 0:
        raise ValueError('"rt_factor" is %s but must be > 0"' % rt_factor)

    env = world.env

    setup_done_events = []
    for sim in world.sims.values():
        if sim.meta["api_version"] >= (2, 2):
            # setup_done() was added in API version 2.2:
            setup_done_events.append(sim.proxy.setup_done())

    yield env.all_of(setup_done_events)

    processes = []
    for sim in world.sims.values():
        process = env.process(
            sim_process(
                world, sim, until, rt_factor, rt_strict, print_progress
            )
        )
        sim.sim_proc = process
        processes.append(process)

    yield env.all_of(processes)


def sim_process(world, sim, until, rt_factor, rt_strict, print_progress):
    """SimPy simulation process for a certain simulator *sim*.

    This method is an exact copy of the current
    :func:`mosaik.scheduler.sim_process` method.

    """
    rt_start = perf_counter()

    try:
        keep_running = get_keep_running_func(world, sim, until)
        while keep_running():
            try:
                yield step_required(world, sim)
            except StopIteration:
                # We've been woken up by a terminating successor.
                # Check if we can also stop or need to keep running.
                continue

            yield wait_for_dependencies(world, sim)
            input_data = get_input_data(world, sim)
            yield from rt_sleep(rt_factor, rt_start, sim, world)
            yield from step(world, sim, input_data)
            rt_check(rt_factor, rt_start, rt_strict, sim)
            yield from get_outputs(world, sim)
            world.sim_progress = get_progress(world.sims, until)
            if print_progress:
                print("Progress: %.2f%%" % world.sim_progress, end="\r")

        # Before we stop, we wake up all dependencies who may be waiting for
        # us. They can then decide whether to also stop of if there's another
        # process left for which they need to provide data.
        for pre_sid in world.df_graph.predecessors(sim.sid):
            evt = world.sims[pre_sid].step_required
            if not evt.triggered:
                evt.fail(StopIteration())

    except ConnectionError as err:
        raise SimulationError(
            f"Simulator '{sim.sid}' closed its connection.", err
        )


def get_input_data(world, sim):
    """Return a dictionary with the input data for *sim*.

    The original function :func:`mosaik.scheduler.get_input_data` is
    called. Afterwards, the :func:`~.trigger_actuators` method of the
    modified world object is called.

    """
    input_data = mosaik.scheduler.get_input_data(world, sim)

    LOG.debug("Now triggering actuators for sim %s", sim.sid)

    # This is the modification for ARL
    world.trigger_actuators(sim, input_data)
    # This was the modification for ARL

    return input_data


def step(world, sim, inputs):
    """Step the scheduler.

    See :func:`mosaik.scheduler.step`.

    """
    return mosaik.scheduler.step(world, sim, inputs)


def get_outputs(world, sim):
    """Get outputs for a simulator.

    See :func:`mosaik.scheduler.get_outputs`.

    """
    return mosaik.scheduler.get_outputs(world, sim)


def get_progress(sims, until):
    """Get simulation progress.

    See :func:`mosaik.scheduler.get_progress`.

    """
    return mosaik.scheduler.get_progress(sims, until)


def rt_sleep(rt_factor, rt_start, sim, world):
    """Sleep for real time simulation.

    See :func:`mosaik.scheduler.rt_sleep`.

    """
    return mosaik.scheduler.rt_sleep(rt_factor, rt_start, sim, world)


def rt_check(rt_factor, rt_start, rt_strict, sim):
    """Check the time for real time simulation.

    See :func:`mosaik.scheduler.rt_check`.

    """
    return mosaik.scheduler.rt_check(rt_factor, rt_start, rt_strict, sim)


def get_keep_running_func(world, sim, until):
    """Return the *keep_running_func*.

    See :func:`mosaik.scheduler.get_keep_running_func`.

    """
    return mosaik.scheduler.get_keep_running_func(world, sim, until)


def step_required(world, sim):
    """Return if another step is required.

    See :func:`mosaik.scheduler.step_required`.

    """
    return mosaik.scheduler.step_required(world, sim)


def wait_for_dependencies(world, sim):
    """Wait for dependencies of *sim*.

    See :func:`mosaik.scheduler.wait_for_dependencies`.

    """
    return mosaik.scheduler.wait_for_dependencies(world, sim)
