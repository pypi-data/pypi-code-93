"""Generator module, implementing facilities for generating circuits using Classiq platform."""
import functools
from enum import Enum
from typing import Optional, Dict

from classiq import api_wrapper, wire
from classiq_interface.generator import (
    constraints,
    result,
    segments,
    function_param_list,
    function_params,
)


# TODO: Add docstrings for auto generated methods.


class Generator:
    """Facility to generate circuits, based on the model."""

    def __init__(self, qubit_count: int, max_depth: int, **kwargs) -> None:
        """Init self with qubit count and maximal depth.

        Args:
            qubit_count (): The number of qubits in the generated circuit.
            max_depth (): The maximum depth of the generated circuit.
        """
        self._constraints = constraints.QuantumCircuitConstraints(
            qubits_count=qubit_count, max_depth=max_depth, **kwargs
        )

    async def generate(self) -> result.GeneratedCircuit:
        """Generates a circuit, based on the aggregation of requirements in self.

        Returns:
            The results of the generation procedure.
        """
        # TODO: There something distorted with regards to the singleton and the configuration. Also, the need to pass
        #       conf here and not in init is weird.
        wrapper = api_wrapper.ApiWrapper()
        generation_result = await wrapper.call_generation_task(self._constraints)

        if generation_result.status != result.GenerationStatus.SUCCESS:
            raise Exception(f"Generation failed: {generation_result.details}")

        return generation_result.details

    @property
    def constraints(self) -> constraints.QuantumCircuitConstraints:
        """Get the constraints aggregated in self.

        Returns:
            The constraints data.
        """
        return self._constraints

    def _add_segment(
        self,
        function: str,
        params: function_params.FunctionParams,
        in_wires: Optional[Dict[Enum, wire.Wire]] = None,
    ) -> Dict[Enum, wire.Wire]:
        if function != type(params).__name__:
            raise Exception("The FunctionParams type does not match function name")

        segment = segments.SegmentInterface(function=function, function_params=params)

        if in_wires:
            for in_enum, in_wire in in_wires.items():
                in_wire.connect_wire(end_segment=segment, input_enum=in_enum)

        self._constraints.segments.append(segment)

        return {
            out_enum: wire.Wire(start_segment=segment, output_enum=out_enum)
            for out_enum in params.get_io_enum(function_params.IO.Output)
        }

    def __getattribute__(self, item):
        is_item_function_name = any(
            item == func.__name__
            for func in function_param_list.get_function_param_list()
        )

        if is_item_function_name:
            return functools.partial(self._add_segment, function=item)

        return super().__getattribute__(item)

    def __dir__(self):
        return list(super().__dir__()) + [
            func.__name__ for func in function_param_list.get_function_param_list()
        ]
