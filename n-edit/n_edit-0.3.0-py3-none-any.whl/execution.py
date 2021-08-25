import abc
import asyncio
import collections
import dataclasses
import typing as t

from n_edit import model

_T = t.TypeVar("_T")


class NodeExecutor(abc.ABC):
    @abc.abstractmethod
    async def execute_node(self, node: model.Node, inputs: dict[str, t.Any]) -> None:
        raise NotImplemented


class LocalExecutor(NodeExecutor):
    def __init__(self, context: t.Any) -> None:
        self.context = context

    async def execute_node(self, node: model.Node, inputs: dict[str, t.Any]) -> None:
        return await node.execute(self.context, **inputs)  # type: ignore


class NodeNotRunnable(Exception):
    pass


@dataclasses.dataclass
class _TaskDefinition:
    node: model.Node
    inputs: dict[str, t.Any]


class Run:
    def __init__(self, graph: model.Graph, node_executor: NodeExecutor) -> None:
        self.graph = graph
        self.node_executor = node_executor
        self.edge_queues: dict[int, collections.deque[t.Any]] = {
            edge_id: collections.deque() for edge_id in self.graph.edges
        }
        self.task_node_id_map: dict[asyncio.Task, int] = {}
        self._tasks_to_create: collections.deque[_TaskDefinition] = collections.deque(
            self._create_task_definition(source_node)
            for source_node in self.graph.source_nodes()
        )
        self.pending_tasks: set[asyncio.Task] = set()

    async def run(self) -> None:
        await self._create_pending_tasks()
        while self.pending_tasks:
            done, self.pending_tasks = await asyncio.wait(
                self.pending_tasks, return_when=asyncio.FIRST_COMPLETED
            )
            for task in done:
                self.handle_finished_task(task)
            await self._create_pending_tasks()

    async def _create_pending_tasks(self) -> None:
        while self._tasks_to_create:
            await self._create_task(self._tasks_to_create.popleft())

    def _append_results(self, node_id: int, results: t.Any) -> None:
        node = self.graph.nodes[node_id]
        if node.has_iterable_output:
            for single_result in results:
                self._append_single_result_to_edges(node_id, single_result)
        else:
            self._append_single_result_to_edges(node_id, results)

    def _append_single_result_to_edges(self, node_id: int, result: t.Any) -> None:
        for edge in self.graph.get_outgoing_edges(node_id):
            self.edge_queues[edge.id_].append(result)

    def handle_finished_task(self, task: asyncio.Task) -> None:
        node_id = self.task_node_id_map[task]
        self._append_results(node_id, task.result())
        while new_tasks := [
            self._create_task_definition(node)
            for node in self.graph.downstream_nodes(node_id)
            if self.is_node_ready(node.id_)
        ]:
            self._tasks_to_create.extend(new_tasks)

    def _create_task_definition(self, node: model.Node) -> _TaskDefinition:
        if not self.is_node_ready(node.id_):
            raise NodeNotRunnable("Node is not ready for execution")
        inputs = self._collect_inputs(node.id_)
        return _TaskDefinition(node, inputs)

    async def _create_task(self, task_definition: _TaskDefinition) -> asyncio.Task:
        name = f"{task_definition.node.type_name}.{task_definition.node.id_}({task_definition.inputs})"
        task = asyncio.create_task(
            self.node_executor.execute_node(
                task_definition.node, task_definition.inputs
            ),
            name=name,
        )
        self.task_node_id_map[task] = task_definition.node.id_
        self.pending_tasks.add(task)
        return task

    def all_edges_ready(self, edge_ids: t.Iterable[int]) -> bool:
        return all(self.edge_queues[edge_id] for edge_id in edge_ids)

    def is_node_ready(self, node_id: int) -> bool:
        all_slots = self.graph.slot_names(node_id)
        input_edges = list(self.graph.get_incoming_edges(node_id).values())
        if not self.all_edges_ready(edge.id_ for edge in input_edges):
            return False
        defaults = self.graph.get_slot_defaults(node_id)
        return not (
            all_slots - {edge.end.name for edge in input_edges} - set(defaults.keys())
        )

    def _collect_inputs(self, node_id: int) -> dict[str, t.Any]:
        input_edges = self.graph.get_incoming_edges(node_id)
        defaults = self.graph.get_slot_defaults(node_id)
        edge_values = {
            slot_name: self.edge_queues[edge.id_].popleft()
            for slot_name, edge in input_edges.items()
        }
        return defaults | edge_values
