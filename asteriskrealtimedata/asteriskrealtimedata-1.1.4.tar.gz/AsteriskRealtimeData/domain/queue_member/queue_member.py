from datetime import datetime
from ipaddress import IPv4Address
from AsteriskRealtimeData.domain.entity import Entity
from dataclasses import dataclass


@dataclass
class QueueMember(Entity):
    peer: str
    actual_status: str
    ipaddress: IPv4Address
    membername: str
    last_status_datetime: datetime = datetime.now()
    is_queuemember: bool = False

    def get_peer(self) -> str:
        return self.peer

    def get_actual_status(self) -> str:
        return self.actual_status

    def get_ipaddress(self) -> IPv4Address:
        return self.ipaddress

    def get_membername(self) -> str:
        return self.membername

    def get_last_status_datetime(self) -> datetime:
        return self.last_status_datetime

    def get_is_queuemember(self):
        return self.is_queuemember

    def as_dict(self) -> dict:
        return self.__repr__()

    def __repr__(self):
        return {
            "id": self.get_id(),
            "peer": self.get_peer(),
            "actual_status": self.get_actual_status(),
            "ipaddress": self.get_ipaddress(),
            "membername": self.get_membername(),
            "last_status_datetime": self.get_last_status_datetime(),
            "is_queuemember": self.get_is_queuemember(),
        }
