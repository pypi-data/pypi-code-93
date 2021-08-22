from typing import List, Optional

import pydantic

from classiq_interface.generator.range_types import NonNegativeIntRange

# TODO figure how to create a pydantic class that can serve as dictionary key
# TODO openapi raises error when using pydantic.constr, need to find solution
# check against duplicates and give better errors
ValidGateName = str


class CustomGateImplementation(pydantic.BaseModel):
    # TODO: add validation for qasm string?
    qasm: str
    n_qubits: pydantic.PositiveInt
    name: Optional[ValidGateName] = None
    depth: Optional[pydantic.PositiveInt] = None


class CustomGate(NonNegativeIntRange):
    implementations: List[CustomGateImplementation]
    add_as_single_gate: bool = True
