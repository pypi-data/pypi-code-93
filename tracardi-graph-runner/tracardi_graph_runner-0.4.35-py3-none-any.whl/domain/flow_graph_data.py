from typing import List

from pydantic import BaseModel
from tracardi_plugin_sdk.domain.register import Plugin


class Position(BaseModel):
    x: int
    y: int


class SimplifiedSpec(BaseModel):
    module: str


class Node(BaseModel):
    id: str
    type: str
    position: Position
    data: Plugin


class Edge(BaseModel):
    source: str
    sourceHandle: str
    target: str
    targetHandle: str
    id: str
    type: str


class FlowGraphData(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
