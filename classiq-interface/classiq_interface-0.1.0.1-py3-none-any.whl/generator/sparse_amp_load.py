from enum import Enum
from typing import Type, List
from classiq_interface.generator.state_preparation import is_power_of_two
import numpy as np

import pydantic

from classiq_interface.generator.complex_type import Complex
from classiq_interface.generator.function_params import FunctionParams


class SparseAmpLoadOutputs(Enum):
    OUTPUT_STATE = "OUTPUT_STATE"


def amplitudes_sum_to_one(amp):
    if round(sum(abs(np.array(amp)) ** 2), 8) != 1:
        raise ValueError("Probabilities do not sum to 1")
    return amp


class SparseAmpLoad(FunctionParams):
    """
    loads a sparse amplitudes vector
    """

    num_qubits: pydantic.PositiveInt = pydantic.Field(
        description="The number of qubits in the circuit."
    )
    amplitudes: List[Complex] = pydantic.Field(description="amplitudes vector to load")

    _is_power_of_two = pydantic.validator("amplitudes", allow_reuse=True)(
        is_power_of_two
    )
    _is_sum_to_one = pydantic.validator("amplitudes", allow_reuse=True)(
        amplitudes_sum_to_one
    )

    _output_names: Type[Enum] = pydantic.PrivateAttr(default=SparseAmpLoadOutputs)
