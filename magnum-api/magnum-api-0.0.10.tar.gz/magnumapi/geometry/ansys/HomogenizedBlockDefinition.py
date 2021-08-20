from dataclasses import dataclass

from magnumapi.geometry.roxie.BlockDefinition import BlockDefinition


@dataclass
class HomogenizedBlockDefinition(BlockDefinition):
    radius_inner: float
    radius_outer: float
    phi_0: float
    phi_1: float
    phi_2: float
    phi_3: float
