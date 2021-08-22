import pydantic
from classiq_interface.generator.circuit_outline import Qubit, Cycle, Clbit


class Cif(pydantic.BaseModel):
    qubit: Qubit
    cycle: Cycle
    clbit: Clbit
    clvalue: bool
