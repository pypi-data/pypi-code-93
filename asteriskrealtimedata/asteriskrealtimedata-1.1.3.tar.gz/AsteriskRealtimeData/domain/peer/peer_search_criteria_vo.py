from typing import Any
from dataclasses import dataclass
from AsteriskRealtimeData.domain.search_by_criteria_vo import SearchByCriteriaVo


@dataclass
class PeerSearchCriteriaVo(SearchByCriteriaVo):
    peer_name: Any = None
    peer_type: Any = None
    peer_ip_address: Any = None

