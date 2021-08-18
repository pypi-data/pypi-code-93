from datetime import datetime
from dataclasses import dataclass
from typing import List
from AsteriskRealtimeData.domain.entity import Entity


@dataclass
class Call(Entity):
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

    def get_peer_name(self) -> str:
        return self.peer_name

    def get_client_id(self) -> str:
        return self.client_id

    def get_dialnumber(self) -> str:
        return self.dialnumber

    def get_lastevent(self) -> datetime:
        return self.lastevent

    def get_track_id(self) -> str:
        return self.track_id

    def get_call_linkedid(self) -> str:
        return self.call_linkedid

    def get_call_actor_address(self) -> str:
        return self.call_actor_address

    def get_event_name(self) -> str:
        return self.event_name

    def get_origin_channel(self) -> str:
        return self.origin_channel

    def get_destination_channel(self) -> str:
        return self.destination_channel

    def get_origin_number(self) -> str:
        return self.origin_number

    def get_destination_number(self) -> str:
        return self.destination_number

    def as_dict(self) -> dict:
        return self.__repr__()

    def __repr__(self):
        return {
            "id": self.get_id(),
            "peer_name": self.get_peer_name(),
            "client_id": self.get_client_id(),
            "dialnumber": self.get_dialnumber(),
            "lastevent": self.get_lastevent(),
            "track_id": self.get_track_id(),
            "call_linkedid": self.get_call_linkedid(),
            "call_actor_address": self.get_call_actor_address(),
            "event_name": self.get_event_name(),
            "origin_channel": self.get_origin_channel(),
            "destination_channel": self.get_destination_channel(),
            "origin_number": self.get_origin_number(),
            "destination_number": self.get_destination_number(),
        }
