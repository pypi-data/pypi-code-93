from datetime import datetime
from ipaddress import IPv4Address
from dataclasses import dataclass


@dataclass
class QueueMemberVo:
    peer: str
    actual_status: str
    ipaddress: IPv4Address
    membername: str
    last_status_datetime: datetime = datetime.now()
    is_queuemember: bool = False

    def as_dict(self) -> dict:
        return self.__repr__()

    def __repr__(self):
        return {
            "peer": self.peer,
            "actual_status": self.actual_status,
            "ipaddress": self.ipaddress,
            "membername": self.membername,
            "last_status_datetime": self.last_status_datetime,
            "is_queuemember": self.is_queuemember,
        }
