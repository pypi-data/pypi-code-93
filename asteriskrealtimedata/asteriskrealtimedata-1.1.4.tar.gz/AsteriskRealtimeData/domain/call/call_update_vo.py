from AsteriskRealtimeData.domain.update_vo import UpdateVo
from dataclasses import dataclass
from typing import Any


@dataclass
class CallUpdateVo(UpdateVo):
    call_linkedid: str
    peer_name: Any = None
    client_id: Any = None
    dialnumber: Any = None
    lastevent: Any = None
    track_id: Any = None
    call_actor_address: Any = None
    event_name: Any = None
    origin_channel: Any = None
    destination_channel: Any = None
    origin_number: Any = None
    destination_number: Any = None
    _update_keys: str = "call_linkedid"
