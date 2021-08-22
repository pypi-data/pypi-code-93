import pydantic
from classiq_interface.generator.circuit_outline import Qubit


class Teleport(pydantic.BaseModel):
    qubit_data: Qubit
    qubit_transmitter: Qubit
    qubit_receiver: Qubit
    num_cifs = 2
