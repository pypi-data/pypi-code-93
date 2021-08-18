from AsteriskRealtimeData.domain.entity import Entity
from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class MascaraIpaddress(Entity):
    ipaddress: str = "0.0.0.0"
    lastconnection: datetime = datetime.now()

    def get_ipaddress(self) -> str:
        return self.ipaddress

    def get_lastconnection(self) -> str:
        return self.lastconnection

    def as_dict(self):
        return self.__repr__()

    def __repr__(self):
        return {"id": self.get_id(), "ipaddress": self.get_ipaddress(), "lastconnection": self.get_lastconnection()}
