from typing import List, Dict
from pydantic import BaseModel

from tracardi_graph_runner.domain.debug_call_info import DebugCallInfo, Profiler
from tracardi_graph_runner.domain.entity import Entity
from tracardi_graph_runner.domain.error_debug_info import ErrorDebugInfo


class FlowDebugInfo(Entity):
    error: List[ErrorDebugInfo] = []


class DebugNodeInfo(BaseModel):
    id: str
    sequenceNumber: int = None
    calls: List[DebugCallInfo] = []
    profiler: Profiler


class DebugInfo(BaseModel):
    timestamp: float
    flow: FlowDebugInfo
    event: Entity
    nodes: Dict[str, DebugNodeInfo] = {}
