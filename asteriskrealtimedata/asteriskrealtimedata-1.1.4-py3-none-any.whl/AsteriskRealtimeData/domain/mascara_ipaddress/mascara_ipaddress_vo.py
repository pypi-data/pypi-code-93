from dataclasses import dataclass
from datetime import datetime


@dataclass
class MascaraIpaddressVo:
    ipaddress: str
    lastconnection: datetime

    def as_dict(self):
        return {"ipaddress": self.ipaddress, "lastconnection": self.lastconnection}
