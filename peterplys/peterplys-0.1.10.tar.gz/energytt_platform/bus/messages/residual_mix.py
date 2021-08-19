from dataclasses import dataclass

from energytt_platform.bus import Message
from energytt_platform.models.residual_mix import \
    ResidualMixEmissions, ResidualMixTechnologyDistribution


@dataclass
class ResidualMixEmissionsUpdate(Message):
    """
    TODO
    """
    emissions: ResidualMixEmissions


@dataclass
class ResidualMixTechnologyDistributionUpdate(Message):
    """
    TODO
    """
    distributions: ResidualMixTechnologyDistribution
