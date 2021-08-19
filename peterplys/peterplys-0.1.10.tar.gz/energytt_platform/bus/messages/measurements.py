from dataclasses import dataclass

from energytt_platform.bus import Message
from energytt_platform.models.measurements import Measurement


@dataclass
class MeasurementUpdate(Message):
    """
    A new Measurement has been added to the system.
    """
    measurement: Measurement


@dataclass
class MeasurementRemoved(Message):
    """
    TODO
    """
    id: str
