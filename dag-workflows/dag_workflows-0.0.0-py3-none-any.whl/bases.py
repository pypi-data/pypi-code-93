"""
Base classes for DAGs and Tasks
"""
from __future__ import annotations

import abc
import dataclasses
import enum
import logging
import os
import typing

import inflection
import networkx
from croniter import croniter

from workflows import outputs

if typing.TYPE_CHECKING:  # pragma: no cover
    from workflows import models

LOGGER = logging.getLogger(__name__)


class RegistrationError(Exception):
    """
    A directory could not be registered as a DAG
    """


class Event(enum.Enum):
    DAG_RUN_START = 0  # dag_run provided
    TASK_RUN_START = 1  # task_run provided
    TASK_START = 2  # task provided
    TASK_FINISH = 3  # task, exception provided
    TASK_RUN_FINISH = 4  # task_run provided
    DAG_RUN_FINISH = 5  # dag_run provided


class DagRegistry:
    """
    A set of DAGs that:
    - prevents overwriting an existing DAG name with the same name
    - stores an exception instead of a DAG but re-raises it on access
    """

    config_module: str = None

    def __init__(self):
        self._dags: typing.Dict[str, DAG] = {}
        self._hooks: typing.List[typing.Callable] = []
        self.worker_config = {}

    def __setitem__(self, k, v):
        if k in self._dags:
            raise RuntimeError(f"Cannot overwrite existing DAG '{k}'")
        self._dags[k] = v
        v.registry = self

    def __getitem__(self, dag_name) -> DAG:
        if dag_name not in self._dags:
            raise KeyError(
                f"DAG '{dag_name}' has not been registered. "
                f"Available DAGs are [{', '.join(self._dags.keys())}]"
            )
        v = self._dags[dag_name]
        if isinstance(v, Exception):
            raise RegistrationError(f"DAG '{dag_name}' failed to load") from v
        return v

    def __iter__(self) -> DAG:
        """Yield valid DAGs, ignoring those that failed to load"""
        yield from [dag for dag in self._dags.values() if not isinstance(dag, Exception)]

    def __str__(self):
        return f"DagRegistry([{', '.join(self._dags.keys())}])"

    def update(self, other):
        for k, v in other._dags.items():  # noqa
            self[k] = v

    def validate(self) -> bool:
        """Check that DAG dependencies are valid"""
        valid = True
        for dag in self:
            for task in dag.tasks(external=True):
                if ":" not in task:
                    continue
                input_dag, input_task = task.split(":")
                try:
                    self[input_dag].get_task(input_task)
                except (KeyError, RegistrationError):
                    LOGGER.warning(f"Input task {task} does not exist")
                    valid = False
        return valid

    def register_hook(self, method):
        """Register a method to be called on state transitions"""
        self._hooks.append(method)

    def call_hooks(
        self,
        event: Event,
        dag: DAG = None,
        task: Task = None,
        dag_run: models.DagRun = None,
        task_run: models.TaskRun = None,
        exception: Exception = None,
    ):
        """
        Call any registered hooks when an event happens.

        The hook is called with additional parameters based on the event type. See the
        comments on ``Event``.
        """
        for hook_method in self._hooks:
            try:
                hook_method(
                    event,
                    dag=dag,
                    task=task,
                    dag_run=dag_run,
                    task_run=task_run,
                    exception=exception,
                )
                LOGGER.debug("Successfully called hook %s on %s", hook_method.__name__, event)
            except Exception as exc:  # noqa
                LOGGER.warning(
                    "Event hook %s failed on %s.", hook_method.__name__, event, exc_info=True
                )


def load_class(type_: str, registry: dict):
    assert type_.lower() == type_, "type name must be all lowercase"
    type_ = inflection.camelize(type_)
    if type_ not in registry:
        allowed = tuple(registry.keys())
        raise AssertionError(f'Type "{type_}" not found in registered types: {allowed}')
    return registry[type_]


@dataclasses.dataclass
class DAG:
    """
    Container for a directed acyclic graph of tasks
    """

    description: str
    folder: str
    schedule: str = None
    graph: networkx.DiGraph = None
    registry: DagRegistry = None
    worker_config: dict = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        self.graph = networkx.DiGraph()
        if self.schedule:
            croniter.expand(self.schedule)  # assert valid

    def __str__(self):
        return f"DAG({self.name})"

    @property
    def name(self):
        return os.path.basename(self.folder)

    def get_task(self, name) -> Task:
        return self.graph.nodes[name]["task"]

    def tasks(self, inputs_to=None, external=False):
        """Return task names, optionally upstream of a task and including
        tasks external to this DAG"""
        tasks = self.graph.predecessors(inputs_to) if inputs_to else self.graph.nodes.keys()
        return [task for task in tasks if ":" not in task or external]

    def validate(self):
        """Check that the graph is acyclical and that all nodes exist as tasks"""
        assert networkx.algorithms.dag.is_directed_acyclic_graph(
            self.graph
        ), "The graph contains cyclical dependencies"
        for name in self.tasks():
            assert (
                "task" in self.graph.nodes[name]
            ), f"Task {name} is used as an input but there is no task file with that name"


# A registry of Task subclasses so they can be found by name when loading task files
TASK_TYPES = {}


@dataclasses.dataclass
class Task(abc.ABC):
    """
    One task within a DAG. A task is 1-1 with a file in the
    DAG folder.
    """

    description: str
    dag: DAG
    name: str
    inputs: typing.List
    outputs: typing.List = dataclasses.field(default_factory=list)
    parameters: typing.List = dataclasses.field(default_factory=list)
    worker_config: dict = dataclasses.field(default_factory=dict)

    # Parameters required by this task type
    class_parameters: typing.ClassVar[tuple] = tuple()

    def __init_subclass__(cls, **kwargs):
        """Register subclasses so they can be found by name"""
        assert cls not in TASK_TYPES, f"Attempted to register {cls.__name__} twice"
        TASK_TYPES[cls.__name__] = cls
        super().__init_subclass__(**kwargs)

    def __post_init__(self):
        self.dag.graph.add_node(self.name, task=self)
        for upstream in self.inputs:
            self.dag.graph.add_edge(upstream, self.name)
        out = []
        for output in self.outputs:
            output_class = load_class(output.pop("type"), outputs.OUTPUT_TYPES)
            out.append(output_class(**output))
        self.outputs = out

    def __str__(self):
        return f"{self.__class__.__name__}({self.dag.name}:{self.name})"

    @abc.abstractmethod
    def execute(self, context: dict):
        """Run the task using the given context"""

    def validate(self, context: dict = None):
        """Run output validations"""
        for output in self.outputs:
            output.validate(context)

    @property
    def all_parameters(self) -> typing.List[str]:
        """parameters required this task"""
        return list(self.class_parameters) + self.parameters
