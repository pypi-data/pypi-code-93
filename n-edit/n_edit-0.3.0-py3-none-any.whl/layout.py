import dataclasses
import json
import typing as t

from n_edit import model, serializable


@dataclasses.dataclass
class Vector:
    x: float
    y: float


@dataclasses.dataclass
class NodeLayout:
    node: model.Node
    position: Vector

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "id": self.node.id_,
            "position": {
                "x": self.position.x,
                "y": self.position.y,
            },
        }


@dataclasses.dataclass
class GraphLayout(serializable.Serializable):
    graph: model.Graph
    nodes: dict[int, NodeLayout] = dataclasses.field(default_factory=dict)

    def add_node(self, node: model.Node, x: float, y: float) -> NodeLayout:
        node_layout = self.nodes[node.id_] = NodeLayout(node, Vector(x, y))
        return node_layout

    def get_node(self, node: model.Node) -> NodeLayout:
        return self.nodes[node.id_]

    def delete_node(self, node: model.Node) -> None:
        try:
            del self.nodes[node.id_]
        except KeyError as e:
            raise model.NodeDoesNotExist("Node is unknown to Layout") from e

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "layout": {
                "nodes": [node.to_dict() for node in self.nodes.values()],
            },
        }

    def load_dict(self, dict_: dict[str, t.Any]) -> None:
        self.nodes = {}
        try:
            for node in dict_["layout"]["nodes"]:
                self.nodes[node["id"]] = NodeLayout(
                    self.graph.nodes[node["id"]],
                    Vector(node["position"]["x"], node["position"]["y"]),
                )
        except KeyError as e:
            raise model.DictInvalid("Invalid Layout") from e
