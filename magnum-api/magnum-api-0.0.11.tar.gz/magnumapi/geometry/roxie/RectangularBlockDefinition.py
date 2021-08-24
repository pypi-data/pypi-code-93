from dataclasses import dataclass

from magnumapi.geometry.roxie.BlockDefinition import BlockDefinition


@dataclass
class RectangularBlockDefinition(BlockDefinition):
    x: float
    y: float
    alpha: float
