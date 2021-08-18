from typing import Any
from dataclasses import dataclass
from AsteriskRealtimeData.domain.search_by_criteria_vo import SearchByCriteriaVo


@dataclass
class QueueMemberSearchCriteriaVo(SearchByCriteriaVo):
    peer: Any = None
    actual_status: Any = None
    ipaddress: Any = None
    membername: Any = None
    last_status_datetime: Any = None
    is_queuemember: Any = None
