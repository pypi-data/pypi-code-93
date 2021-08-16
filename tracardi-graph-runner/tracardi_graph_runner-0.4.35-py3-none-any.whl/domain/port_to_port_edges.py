from typing import Tuple

from pydantic import BaseModel

from .edge import Edge
from .edges import Edges


class PortToPortEdges(BaseModel):

    edges: dict = {}

    def __iter__(self) -> Tuple[str, Edge, str]:
        for start, edges in self.edges.items():  # type: str, Edges
            for edge in edges:
                yield edge.source.param, edge, edge.target.param

    def __len__(self):
        i = 0
        for _, edges in self.edges.items():
            i += len(edges)
        return i

    def add(self, edge: Edge):
        if edge.source.param not in self.edges:
            self.edges[edge.source.param] = set()
        self.edges[edge.source.param].add(edge)

    def dict(self, **kwargs):
        for key, edge in self.edges.items():  # type: Edge
            self.edges[key] = list(self.edges[key])
        return super().dict(**kwargs)

    def get_start_ports(self):
        return self.edges.keys()



