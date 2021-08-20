from dataclasses import dataclass

from magnumapi.geometry.roxie.CosThetaBlockDefinition import CosThetaBlockDefinition


@dataclass
class RelativeCosThetaBlockDefinition(CosThetaBlockDefinition):
    phi_r: float
    alpha_r: float
