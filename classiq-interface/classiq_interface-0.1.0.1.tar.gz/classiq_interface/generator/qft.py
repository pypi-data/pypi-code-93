from enum import Enum
from typing import Type

import pydantic

from classiq_interface.generator import function_params


class QftInputs(Enum):
    IN = "IN"


QftOutputs = function_params.DefaultOutputNames


class QFT(function_params.FunctionParams):
    """
    Creates a quantum Fourier transform on a specified number of qubits.
    Use the inverse flag to create the inverse QFT circuit.
    """

    num_qubits: pydantic.PositiveInt = pydantic.Field(
        description="The number of qubits on which the QFT acts."
    )
    approximation_degree: pydantic.conint(ge=0) = pydantic.Field(
        default=0,
        description="The degree of approximation (0 for no approximation). The smallest "
        "'approximation_degree' rotation angles are dropped from the QFT.",
    )
    do_swaps: bool = pydantic.Field(
        default=True, description="Whether to include the final swaps in the QFT."
    )
    inverse: bool = pydantic.Field(
        default=False,
        description="If True, the inverse Fourier transform is constructed.",
    )

    _input_names: Type[Enum] = pydantic.PrivateAttr(default=QftInputs)
    _output_names: Type[Enum] = pydantic.PrivateAttr(default=QftOutputs)
