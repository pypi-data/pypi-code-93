from typing import List
from AsteriskRealtimeData.domain.call.call_search_criteria_vo import CallSerchCriteriaVo
from AsteriskRealtimeData.domain.call.call_update_vo import CallUpdateVo
from AsteriskRealtimeData.application.call_service import CallService
from AsteriskRealtimeData.domain.call.call_vo import CallVo


class CallController:
    def create(self, call_vo: CallVo) -> CallVo:
        return CallService().create_call(call_vo)

    def update(self, call_update_vo: CallUpdateVo) -> CallVo:
        return CallService().update_call(call_update_vo)

    def get_all(self) -> List[CallVo]:
        calls = CallService().call_list()
        result: list = []

        for call in calls:
            result.append(call)

        return result

    def get_by_call_linkedid(self, call_linkedid: str) -> CallVo:
        return CallService().get_call(call_linkedid)

    def get_by_search_criteria(self, search_criteria: CallSerchCriteriaVo) -> CallVo:
        return CallService().get_by_search_criteria(search_criteria)

    def delete_by_call_linkedid(self, call_linkedid: str) -> None:
        CallService().delete_call(call_linkedid)
