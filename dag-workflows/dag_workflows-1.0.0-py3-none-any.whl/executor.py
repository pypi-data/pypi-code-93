"""
Execute tasks from a DAG
"""
import logging
import os
import typing

import networkx

from workflows import bases

LOGGER = logging.getLogger(__name__)


class Context:
    """Run context for a task, allowing parameters to be passed in.

    Parameters have string keys. They cannot be overwritten.
    When a task is executed, it is given a copy of the context so any changes
    made are not preserved. Tasks can return a value which is stored in
    with the key being the task name.
    """

    def __init__(self):
        self._data = {}

    def set(self, key, value):
        """Set the value for a parameter"""
        assert isinstance(key, str)
        assert self._data.get(key) is None
        self._data[key] = value

    def copy(self, parameters: list):
        """A shallow copy of the parameters for a single task"""
        return {k: self._data[k] for k in parameters}

    def check_required(self):
        """Check that all configured parameters have been given a value"""
        unassigned = [key for key, value in self._data.items() if value is None]
        assert (
            not unassigned
        ), f"Cannot run the DAG because there are missing parameters: {unassigned}"


def execute_dag(dag: bases.DAG, begin: str = None, end: str = None):
    """Run tasks from a DAG, optionally constrained to a given range of tasks"""
    tasks = get_sorted_tasks(dag.graph, begin, end)

    # get all required parameters for the nodes
    context = Context()
    parameters = set([param for task in tasks for param in task.all_parameters])
    for param in parameters:
        # maybe allow parameters to be passed on the command line
        context.set(param, os.environ.get(param))
    context.check_required()

    # go through nodes and execute
    for task in tasks:
        LOGGER.info("Running task %s", task.name)
        dag.registry.call_hooks(bases.Event.TASK_START, task=task)
        try:
            task.execute(context.copy(task.all_parameters))
        except Exception as exc:
            dag.registry.call_hooks(bases.Event.TASK_FINISH, task=task, exception=exc)
            raise
        dag.registry.call_hooks(bases.Event.TASK_FINISH, task=task)


def get_sorted_tasks(
    graph: networkx.DiGraph, begin: str = None, end: str = None
) -> typing.List[bases.Task]:
    """Given a graph and optional begin and end node names, create a subgraph"""
    if begin and end and begin == end:
        assert (
            begin in graph.nodes
        ), f"Invalid task name '{begin}'. Available tasks are {graph.nodes}"
        graph = graph.subgraph([begin])
    else:
        if begin:
            assert (
                begin in graph.nodes
            ), f"Invalid task name {begin}. Available tasks are {graph.nodes}"
            graph = graph.subgraph([begin, *graph.successors(begin)])
        if end:
            assert (
                end in graph.nodes
            ), f"Invalid task name {end}. Available tasks are {graph.nodes}"
            graph = graph.subgraph([end, *graph.predecessors(end)])
    return [
        graph.nodes.get(node)["task"]
        for node in networkx.algorithms.dag.lexicographical_topological_sort(graph)
        if ":" not in node  # the task is external to this DAG
    ]
