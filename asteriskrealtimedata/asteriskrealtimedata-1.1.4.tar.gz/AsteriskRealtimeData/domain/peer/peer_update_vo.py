from dataclasses import dataclass
from ipaddress import IPv4Address
from typing import Any
from AsteriskRealtimeData.domain.update_vo import UpdateVo


@dataclass
class PeerUpdateVo(UpdateVo):
    peer_name: str
    peer_type: Any = None
    peer_ip_address: IPv4Address = None
    _update_keys: str = "peer_name"

