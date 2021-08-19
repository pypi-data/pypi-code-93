from dataclasses import dataclass

from energytt_platform.bus import Message
from energytt_platform.models.tech import Technology, TechnologyCodes


@dataclass
class TechnologyUpdate(Message):
    """
    A Technology has been added or updated.
    """
    technology: Technology


@dataclass
class TechnologyRemoved(Message):
    """
    TODO
    """
    codes: TechnologyCodes
