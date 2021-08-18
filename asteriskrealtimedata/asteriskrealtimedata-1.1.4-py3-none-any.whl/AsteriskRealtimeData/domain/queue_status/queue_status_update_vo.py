from AsteriskRealtimeData.domain.update_vo import UpdateVo
from dataclasses import dataclass
from typing import Any


@dataclass
class QueueStatusUpdateVo(UpdateVo):
    status_code: str
    description: Any = None
    _update_keys: str = "status_code"
