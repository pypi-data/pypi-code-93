from typing import Any
from dataclasses import dataclass
from AsteriskRealtimeData.domain.search_by_criteria_vo import SearchByCriteriaVo


@dataclass
class PauseReasonSearchCriteriaVo(SearchByCriteriaVo):
    pause_code: Any = None
    description: Any = None
    paused: Any = None
