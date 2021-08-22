from enum import Enum
from typing import Type, List
import numpy as np

import pydantic

from classiq_interface.generator.complex_type import Complex
from classiq_interface.generator.function_params import FunctionParams
from classiq_interface.generator.sparse_amp_load import amplitudes_sum_to_one
from classiq_interface.generator.state_preparation import is_power_of_two


class HadamardAmpLoadOutputs(Enum):
    OUTPUT_STATE = "OUTPUT_STATE"


class HadamardAmpLoad(FunctionParams):
    """
    loads a amplitudes vector using hadamard decomposition
    """

    num_qubits: pydantic.PositiveInt = pydantic.Field(
        description="The number of qubits in the circuit."
    )
    amplitudes: List[Complex] = pydantic.Field(description="amplitudes vector to load")

    cutoff: pydantic.conint(ge=1) = pydantic.Field(
        description="The number of hadamard coefficients to keep. "
        "The largest cutoff_num coefficients are used to load the amplitudes"
    )

    _is_power_of_two = pydantic.validator("amplitudes", allow_reuse=True)(
        is_power_of_two
    )
    _is_sum_to_one = pydantic.validator("amplitudes", allow_reuse=True)(
        amplitudes_sum_to_one
    )

    @pydantic.root_validator()
    def cutoff_validator(cls, values):
        amp = values.get("amplitudes")
        cutoff = values.get("cutoff")
        if cutoff > len(amp):
            raise ValueError(
                "cutoff number should be smaller or equal to the length of the amplitudes vector "
            )
        return values

    _output_names: Type[Enum] = pydantic.PrivateAttr(default=HadamardAmpLoadOutputs)
