from enum import Enum

from classiq_interface.generator import segments


class Wire:
    def __init__(self, start_segment: segments.SegmentInterface, output_enum: Enum):
        self._start_seg = start_segment
        self._start_enum = output_enum
        self._wire_name = f"{self._start_seg.name}_{self._start_enum.name}"

    def connect_wire(self, end_segment: segments.SegmentInterface, input_enum: Enum):
        self._start_seg.outputs[self._start_enum.name] = self._wire_name
        end_segment.inputs[input_enum.name] = self._wire_name
