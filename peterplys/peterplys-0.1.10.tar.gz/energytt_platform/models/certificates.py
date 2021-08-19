from datetime import datetime
from dataclasses import dataclass

from energytt_platform.serialize import Serializable


@dataclass
class GranularCertificate(Serializable):
    """
    A single Granular Certificate.
    """
    id: str
    issued: datetime
    expires: datetime
    begin: datetime
    end: datetime
    sector: str
    amount: int
    technology_code: str
    fuel_code: str
