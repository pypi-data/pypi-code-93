from dataclasses import dataclass
from ipaddress import IPv4Address


@dataclass
class PeerVo:
    peer_name: str
    peer_type: str
    peer_ip_address: IPv4Address

    def as_dict(self):
        return self.__repr__()

    def __repr__(self):
        return {
            "peer_name": self.peer_name,
            "peer_type": self.peer_type,
            "peer_ip_address": self.peer_ip_address,
        }
