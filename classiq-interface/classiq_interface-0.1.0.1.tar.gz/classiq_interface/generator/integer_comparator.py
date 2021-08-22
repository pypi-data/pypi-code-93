from enum import Enum
from typing import Type

import pydantic
from classiq_interface.generator.function_params import FunctionParams


class IntegerComparatorInputs(Enum):
    ARGUMENT_IN = "ARGUMENT_IN"
    TARGET_QUBIT = "TARGET_QUBIT"


class IntegerComparatorOutputs(Enum):
    ARGUMENT_OUT = "ARGUMENT_OUT"
    COMPARISON_RESULT = "COMPARISON_RESULT"


class IntegerComparator(FunctionParams):
    """
    Compares basis states |i> against a given integer n.
     if greater_or_equal = True, the target qubit is flipped if i is greater or equal to n
     if greater_or_equal = False, the target qubit is flipped if i is smaller than n
    """

    num_qubits: pydantic.PositiveInt = pydantic.Field(
        description="The number of qubits describing the input state."
    )
    comparand: int = pydantic.Field(description="integer to compare with")
    greater_or_equal: bool = pydantic.Field(
        default=True,
        description="if True, evaluates if input state is >= than given integer,"
        " otherwise <",
    )

    _input_names: Type[Enum] = pydantic.PrivateAttr(default=IntegerComparatorInputs)
    _output_names: Type[Enum] = pydantic.PrivateAttr(default=IntegerComparatorOutputs)
