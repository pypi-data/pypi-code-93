from typing import List, Optional
from pydantic import BaseModel
from tracardi_plugin_sdk.action_runner import ActionRunner

from .port_to_port_edges import PortToPortEdges


class Graph(BaseModel):
    in_edges: PortToPortEdges = PortToPortEdges()
    out_edges: PortToPortEdges = PortToPortEdges()


class Node(BaseModel):
    id: str
    start: Optional[bool] = False
    debug: bool = False
    inputs: Optional[List[str]] = []
    outputs: Optional[List[str]] = []
    className: str
    module: str
    init: Optional[dict] = {}
    object: Optional[ActionRunner] = None
    graph: Graph = Graph()

    class Config:
        arbitrary_types_allowed = True

