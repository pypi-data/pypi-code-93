from typing import Any
from dataclasses import dataclass
from AsteriskRealtimeData.domain.search_by_criteria_vo import SearchByCriteriaVo


@dataclass
class CallSerchCriteriaVo(SearchByCriteriaVo):
    call_linkedid: Any = None
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
