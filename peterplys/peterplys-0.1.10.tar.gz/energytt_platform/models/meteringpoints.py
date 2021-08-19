from typing import Optional
from dataclasses import dataclass, field

from energytt_platform.serialize import Serializable
from energytt_platform.models.tech import Technology

from .common import EnergyDirection, Address


MeteringPointType = EnergyDirection


@dataclass
class MeteringPoint(Serializable):
    """
    TODO
    """
    gsrn: str
    type: Optional[MeteringPointType] = field(default=None)
    sector: Optional[str] = field(default=None)
    technology: Optional[Technology] = field(default=None)
    address: Optional[Address] = field(default=None)


@dataclass
class MeteringPointDelegate(Serializable):
    """
    An actor (identified by its subject) who has been delegated
    access to a MeteringPoint (identified by its GSRN number).
    """
    gsrn: str
    subject: str
