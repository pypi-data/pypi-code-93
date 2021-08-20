from dataclasses import dataclass

from magnumapi.geometry.roxie.CosThetaBlockDefinition import CosThetaBlockDefinition


@dataclass
class AbsoluteCosThetaBlockDefinition(CosThetaBlockDefinition):
    phi: float
    alpha: float
