from dataclasses import dataclass

from magnumapi.geometry.roxie.BlockDefinition import BlockDefinition


@dataclass
class CosThetaBlockDefinition(BlockDefinition):
    radius: float
