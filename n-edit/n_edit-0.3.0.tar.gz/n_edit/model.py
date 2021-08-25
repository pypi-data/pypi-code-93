from __future__ import annotations

import collections.abc
import dataclasses
import inspect
import itertools
import typing as t

from n_edit import serializable


class ModelError(Exception):
    pass


class NodeDoesNotExist(ModelError):
    pass


class NodeClassInvalid(ModelError):
    pass


class UnknownNodeType(ModelError):
    pass


class EdgeDoesNotExist(ModelError):
    pass


class SlotDoesNotExist(ModelError):
    pass


class SlotHasNoDefault(ModelError):
    pass


class ValidationError(ModelError):
    pass


class EdgeInvalid(ValidationError):
    pass


class DictInvalid(ModelError):
    pass


class InvalidNodeType(ModelError):
    pass


def next_free_key(dict_: dict[int, t.Any]) -> int:
    return next(i for i in itertools.count() if i not in dict_)


_NodeClass = t.TypeVar("_NodeClass", bound=type)


class NodeLibrary:
    def __init__(self, node_types: t.Optional[list[t.Type[Node]]] = None) -> None:
        node_types = node_types or []
        self._node_types = {
            node_type.type_name(): node_type for node_type in node_types
        }

    def get_node_type(self, type_name: str) -> t.Type[Node]:
        try:
            return self._node_types[type_name]
        except IndexError as e:
            raise UnknownNodeType(f"The node type {type_name} does not exist") from e

    def known_types(self) -> t.Iterable[str]:
        return self._node_types.keys()

    def node(self, klass: _NodeClass) -> _NodeClass:
        if not issubclass(klass, Node):
            raise InvalidNodeType("Must be a subclass of Node")
        self._node_types[klass.type_name()] = klass
        return klass  # type: ignore


@dataclasses.dataclass
class Graph(serializable.Serializable):
    node_library: NodeLibrary
    nodes: dict[int, Node] = dataclasses.field(default_factory=dict)
    edges: dict[int, Edge] = dataclasses.field(default_factory=dict)

    def create_node(self, node_type: str, id_: t.Optional[int] = None) -> Node:
        if id_ is None:
            id_ = next_free_key(self.nodes)
        new_node = self.nodes[id_] = self.node_library.get_node_type(node_type)(id_)
        return new_node

    def delete_node(self, node_id: int) -> None:
        try:
            del self.nodes[node_id]
        except KeyError:
            raise NodeDoesNotExist(
                f"Can't delete node {node_id} because it does not exist."
            )

    def create_edge(
        self, start: OutputSlot, end: InputSlot, id_: t.Optional[int] = None
    ) -> Edge:
        if id_ is None:
            id_ = next_free_key(self.edges)
        new_edge = self.edges[id_] = Edge(id_, start, end)
        return new_edge

    def delete_edge(self, edge_id: int) -> None:
        try:
            del self.edges[edge_id]
        except KeyError:
            raise EdgeDoesNotExist(
                f"Can't delete edge {edge_id} because it does not exist."
            )

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges.values()],
        }

    def clear(self) -> None:
        self.nodes = {}
        self.edges = {}

    def set_input_value(self, node_id: int, input_slot: str, value: t.Any) -> None:
        slot = self.nodes[node_id].get_input_slot(input_slot)
        if not isinstance(slot, DefaultInputSlot):
            raise SlotHasNoDefault(f"Can't set default on non default slot")
        slot.value = value

    def load_dict(self, dict_: dict[str, t.Any]) -> None:
        self.clear()
        try:
            for node_dict in dict_["nodes"]:
                node = self.create_node(node_dict["type"], node_dict["id"])
                for slot_name, value in node_dict["defaults"].items():
                    self.set_input_value(node.id_, slot_name, value)
            for edge_dict in dict_["edges"]:
                edge_id = edge_dict["id"]
                start_slot = self.nodes[edge_dict["start"]["id"]].output
                end_slot = self.nodes[edge_dict["end"]["id"]].get_input_slot(
                    edge_dict["end"]["slot"]
                )
                self.create_edge(start_slot, end_slot, edge_id)
        except KeyError as e:
            raise DictInvalid from e

    def source_nodes(self) -> list[Node]:
        connected_node_ids = {edge.end.owner.id_ for edge in self.edges.values()}
        all_node_ids = {node.id_ for node in self.nodes.values()}
        candidates = (self.nodes[id_] for id_ in all_node_ids - connected_node_ids)
        return [node for node in candidates if node.all_slots_have_default()]

    def get_incoming_edges(self, node_id: int) -> dict[str, Edge]:
        return {
            edge.end.name: edge
            for edge in self.edges.values()
            if edge.end.owner.id_ == node_id
        }

    def get_outgoing_edges(self, node_id: int) -> list[Edge]:
        return [edge for edge in self.edges.values() if edge.start.owner.id_ == node_id]

    def get_slot_defaults(self, node_id: int) -> dict[str, t.Any]:
        return self.nodes[node_id].get_defaults()

    def slot_names(self, node_id: int) -> set[str]:
        return self.nodes[node_id].slot_names()

    def downstream_nodes(self, node_id: int) -> list[Node]:
        return [edge.end.owner for edge in self.get_outgoing_edges(node_id)]


_T = t.TypeVar("_T")


@dataclasses.dataclass
class Node(t.Generic[_T]):
    id_: int

    _RESERVED_NAMES = ("return", "context")

    def __post_init__(self) -> None:
        self.inputs: list[t.Union[InputSlot, DefaultInputSlot]] = self._create_inputs()
        self.has_iterable_output = False
        self.output = self._create_output()

    def _create_inputs(self) -> list[t.Union[InputSlot, DefaultInputSlot]]:
        params = inspect.signature(self.execute).parameters
        return [  # type: ignore
            DefaultInputSlot(name, type_, self, params[name].default)
            for name, type_ in t.get_type_hints(self.execute).items()
            if name not in self._RESERVED_NAMES
            and params[name].default is not inspect.Parameter.empty
        ] + [
            InputSlot(name, type_, self)  # type: ignore
            for name, type_ in t.get_type_hints(self.execute).items()
            if name not in self._RESERVED_NAMES
            and params[name].default is inspect.Parameter.empty
        ]

    def _create_output(self) -> OutputSlot:
        execute_return_type = t.get_type_hints(self.execute)["return"]
        if t.get_origin(execute_return_type) is collections.abc.Iterable:
            args = t.get_args(execute_return_type)
            try:
                output_type = args[0]
            except IndexError:
                raise NodeClassInvalid("The return type is ill defined")
            else:
                self.has_iterable_output = True
        else:
            output_type = execute_return_type
        return OutputSlot(output_type, self)

    @classmethod
    def execute(cls, context: t.Any) -> _T:
        raise NotImplemented

    def get_input_slot(self, name: str) -> InputSlot:
        for slot in self.inputs:
            if slot.name == name:
                return slot
        raise SlotDoesNotExist(f"This node has no slot {name}")

    @classmethod
    def type_name(cls) -> str:
        return cls.__name__

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "id": self.id_,
            "type": self.type_name(),
            "defaults": self.get_defaults(),
        }

    def get_defaults(self) -> dict[str, t.Any]:
        return {
            input_slot.name: input_slot.value
            for input_slot in self.inputs
            if isinstance(input_slot, DefaultInputSlot)
        }

    def all_slots_have_default(self) -> bool:
        return all(slot.has_default() for slot in self.inputs)

    def slot_names(self) -> set[str]:
        return {slot.name for slot in self.inputs}


@dataclasses.dataclass
class InputSlot(t.Generic[_T]):
    name: str
    data_type: t.Type[_T]
    owner: Node

    def has_default(self) -> bool:
        return False


@dataclasses.dataclass
class DefaultInputSlot(InputSlot[_T]):
    value: _T

    def has_default(self) -> bool:
        return True


@dataclasses.dataclass
class OutputSlot(t.Generic[_T]):
    data_type: t.Type[_T]
    owner: Node


@dataclasses.dataclass
class Edge:
    id_: int
    start: OutputSlot
    end: InputSlot

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "id": self.id_,
            "start": {
                "id": self.start.owner.id_,
            },
            "end": {
                "id": self.end.owner.id_,
                "slot": self.end.name,
            },
        }
