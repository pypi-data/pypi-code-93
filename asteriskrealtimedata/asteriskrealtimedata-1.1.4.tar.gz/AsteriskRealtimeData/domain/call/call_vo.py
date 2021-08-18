from datetime import datetime
from dataclasses import dataclass


@dataclass
class CallVo:
    peer_name: str
    client_id: str
    dialnumber: str
    lastevent: datetime
    track_id: str
    call_linkedid: str
    call_actor_address: str
    event_name: str
    origin_channel: str
    destination_channel: str
    origin_number: str
    destination_number: str

    def as_dict(self) -> dict:
        return self.__repr__()

    def __repr__(self):
        return {
            "peer_name": self.peer_name,
            "client_id": self.client_id,
            "dialnumber": self.dialnumber,
            "lastevent": self.lastevent,
            "track_id": self.track_id,
            "call_linkedid": self.call_linkedid,
            "call_actor_address": self.call_actor_address,
            "event_name": self.event_name,
            "origin_channel": self.origin_channel,
            "destination_channel": self.destination_channel,
            "origin_number": self.origin_number,
            "destination_number": self.destination_number,
        }
