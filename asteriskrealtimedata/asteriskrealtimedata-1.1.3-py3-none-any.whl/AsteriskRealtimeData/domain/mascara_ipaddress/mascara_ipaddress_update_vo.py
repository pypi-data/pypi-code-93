from AsteriskRealtimeData.domain.update_vo import UpdateVo
from dataclasses import dataclass
from typing import Any
from datetime import datetime


@dataclass
class MascaraIpaddressUpdateVo(UpdateVo):
    ipaddress: str
    lastconnection: Any = None
    _update_keys: str = "ipaddress"
