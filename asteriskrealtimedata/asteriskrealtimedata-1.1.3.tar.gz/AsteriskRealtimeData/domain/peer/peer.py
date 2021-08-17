from dataclasses import dataclass
from ipaddress import IPv4Address
from AsteriskRealtimeData.domain.entity import Entity


@dataclass
class Peer(Entity):
    peer_name: str
    peer_type: str
    peer_ip_address: IPv4Address

    def get_peer_name(self) -> str:
        return self.peer_name

    def get_peer_type(self) -> str:
        return self.peer_type

    def get_peer_ip_address(self) -> IPv4Address:
        return self.peer_ip_address

    def as_dict(self):
        return self.__repr__()

    def __repr__(self):
        return {
            "id": self.id,
            "peer_name": self.get_peer_name(),
            "peer_type": self.get_peer_type(),
            "peer_ip_address": self.get_peer_ip_address(),
        }

