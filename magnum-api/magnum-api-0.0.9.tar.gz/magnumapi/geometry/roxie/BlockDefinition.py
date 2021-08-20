from dataclasses import dataclass


@dataclass
class BlockDefinition:
    no: int
    type: int
    nco: int
    current: float
    condname: str
    n1: int
    n2: int
    imag: float
    turn: float