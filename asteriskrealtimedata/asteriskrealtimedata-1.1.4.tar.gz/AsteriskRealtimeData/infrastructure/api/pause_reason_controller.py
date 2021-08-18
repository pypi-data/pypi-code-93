from typing import List
from AsteriskRealtimeData.domain.pause_reason.pause_reason_search_criteria_vo import PauseReasonSearchCriteriaVo
from AsteriskRealtimeData.domain.pause_reason.pause_reason_update_vo import PauseReasonUpdateVo
from AsteriskRealtimeData.application.pause_reasons_service import PauseReasonService
from AsteriskRealtimeData.domain.pause_reason.pause_reasons_vo import PauseReasonVo


class PauseReasonController:
    def create(self, pause_reason_vo: PauseReasonVo) -> PauseReasonVo:
        return PauseReasonService().create_pause_reason(pause_reason_vo)

    def update(self, pause_reason_update_vo: PauseReasonUpdateVo) -> PauseReasonVo:
        return PauseReasonService().update_pause_reason(pause_reason_update_vo)

    def get_all(self) -> List[PauseReasonVo]:
        pause_reasons = PauseReasonService().pause_reason_list()
        result: list = []

        for pause_reason in pause_reasons:
            result.append(pause_reason)

        return result

    def get_by_pause_code(self, pause_code: str) -> PauseReasonVo:
        return PauseReasonService().get_pause_reason(pause_code)

    def get_by_search_criteria(self, search_criteria: PauseReasonSearchCriteriaVo) -> PauseReasonVo:
        return PauseReasonService().get_by_search_criteria(search_criteria)

    def delete_by_pause_code(self, pause_code: str) -> None:
        PauseReasonService().delete_pause_reason(pause_code)
