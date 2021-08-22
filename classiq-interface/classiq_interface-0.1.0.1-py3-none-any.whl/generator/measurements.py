import pydantic
from classiq_interface.generator.circuit_outline import Qubit, Cycle


class Measurement(pydantic.BaseModel):
    qubit: Qubit
    cycle: Cycle
