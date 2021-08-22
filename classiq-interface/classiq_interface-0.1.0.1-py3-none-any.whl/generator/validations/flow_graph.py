from collections import defaultdict
from dataclasses import dataclass
from typing import List, Optional, Dict
from itertools import chain
import networkx as nx
import pydantic
from classiq_interface.generator.segments import SegmentInterface

IO_MULTI_USE_ERROR_MSG = "Input and output names can only be used once"
IO_NAME_MISMATCH_ERROR_MSG = "Inputs and outputs are not identical"


@dataclass
class Wire:
    start: Optional[pydantic.constr(min_length=1)] = None
    end: Optional[pydantic.constr(min_length=1)] = None


def _parse_segment_inputs(segment: SegmentInterface, wires: Dict[str, Wire]) -> None:
    if not segment.inputs:
        return

    for wire_name in segment.inputs.values():
        wire = wires[wire_name]

        if wire.end:
            raise ValueError(
                IO_MULTI_USE_ERROR_MSG
                + f". The name {wire_name} is used multiple times."
            )
        wire.end = segment.name


def _parse_segment_outputs(segment: SegmentInterface, wires: Dict[str, Wire]) -> None:
    if not segment.outputs:
        return

    for wire_name in segment.outputs.values():
        wire = wires[wire_name]

        if wire.start:
            raise ValueError(
                IO_MULTI_USE_ERROR_MSG
                + f". The name {wire_name} is used multiple times."
            )
        wire.start = segment.name


def create_flow_graph(segment_list: List[SegmentInterface]) -> nx.DiGraph:
    input_names = sorted(
        chain(*[segment.inputs.values() for segment in segment_list if segment.inputs])
    )
    output_names = sorted(
        chain(
            *[segment.outputs.values() for segment in segment_list if segment.outputs]
        )
    )

    if not input_names == output_names:
        raise ValueError(IO_NAME_MISMATCH_ERROR_MSG)

    wires = defaultdict(Wire)
    for segment in segment_list:
        _parse_segment_inputs(segment, wires)
        _parse_segment_outputs(segment, wires)

    edges = [(wire.start, wire.end) for wire in wires.values()]

    graph = nx.DiGraph()

    graph.add_nodes_from(
        [(segment.name, {"data": segment}) for segment in segment_list]
    )
    graph.add_edges_from(edges)

    return graph
