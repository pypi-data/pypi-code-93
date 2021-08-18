from AsteriskRealtimeData.domain.update_vo import UpdateVo
from dataclasses import dataclass
from typing import Any


@dataclass
class QueueMemberUpdateVo(UpdateVo):
    peer: str
    actual_status: Any = None
    ipaddress: Any = None
    membername: Any = None
    last_status_datetime: Any = None
    is_queuemember: Any = None
    _update_keys: str = "peer"
