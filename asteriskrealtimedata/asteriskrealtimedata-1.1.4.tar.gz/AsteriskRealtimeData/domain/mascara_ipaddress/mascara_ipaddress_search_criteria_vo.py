from typing import Any
from dataclasses import dataclass
from AsteriskRealtimeData.domain.search_by_criteria_vo import SearchByCriteriaVo


@dataclass
class MascaraIpaddressSearchCriteriaVo(SearchByCriteriaVo):
    ipaddress: Any = None
    lastconnection: Any = None
