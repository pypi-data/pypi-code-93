from typing import Any
from dataclasses import dataclass
from AsteriskRealtimeData.domain.search_by_criteria_vo import SearchByCriteriaVo


@dataclass
class QueueStatusSearchCriteriaVo(SearchByCriteriaVo):
    status_code: Any = None
    description: Any = None
