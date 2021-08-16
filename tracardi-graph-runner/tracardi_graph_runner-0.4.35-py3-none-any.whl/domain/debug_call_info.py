from typing import List, Optional

from pydantic import BaseModel
from tracardi_plugin_sdk.domain.console import Console

from tracardi_graph_runner.domain.entity import Entity
from tracardi_graph_runner.domain.input_params import InputParams
from tracardi_graph_runner.domain.action_result import ActionResult


class DebugInput(BaseModel):
    edge: Optional[Entity] = None
    params: Optional[InputParams] = None


class DebugOutput(BaseModel):
    edge: Optional[Entity] = None
    results: Optional[List[ActionResult]] = None


class Profiler(BaseModel):
    startTime: float
    runTime: float
    endTime: float


class DebugCallInfo(BaseModel):
    profiler: Profiler
    input: DebugInput
    output: DebugOutput
    init: Optional[dict] = None
    profile: Optional[dict] = {}
    error: Optional[str] = None
    console: Optional[Console] = None
    run: bool = False
