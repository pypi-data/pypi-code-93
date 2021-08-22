from enum import Enum
from typing import Optional, List, Union

import pydantic
from classiq_interface.generator.custom_gates import ValidGateName


class UnrollerType(str, Enum):
    THREE_QUBIT_GATES = "three_qubit_gates"


class TranspilationPreferences(pydantic.BaseModel):
    """
    Preferences for running transpiler on the generated quantum circuit.
    """

    is_sub_circuit: bool = pydantic.Field(
        default=False,
        description="Whether the transpiled circuit is part of a bigger circuit. "
        "This enables optimizations with assumptions on the start and end conditions of the circuit.",
    )
    unroller: Optional[Union[UnrollerType, List[ValidGateName]]] = pydantic.Field(
        default=None,
        description=f"Unroll {UnrollerType.THREE_QUBIT_GATES} or unroll to specific basis gates.",
    )

    @pydantic.validator("unroller")
    def validate_unroller(cls, unroller):
        if isinstance(unroller, list) and not unroller:
            raise ValueError("Empty basis gates is forbidden.")

        return unroller
