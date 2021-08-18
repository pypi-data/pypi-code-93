from AsteriskRealtimeData.domain.update_vo import UpdateVo
from dataclasses import dataclass
from typing import Any


@dataclass
class PauseReasonUpdateVo(UpdateVo):
    pause_code: str
    description: Any = None
    paused: Any = None
    _update_keys: str = "pause_code"
