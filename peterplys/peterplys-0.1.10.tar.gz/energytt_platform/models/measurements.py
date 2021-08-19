from datetime import datetime
from dataclasses import dataclass

from energytt_platform.serialize import Serializable

from .common import EnergyDirection


MeasurementType = EnergyDirection


@dataclass
class Measurement(Serializable):
    id: str
    gsrn: str
    amount: int
    begin: datetime
    end: datetime
