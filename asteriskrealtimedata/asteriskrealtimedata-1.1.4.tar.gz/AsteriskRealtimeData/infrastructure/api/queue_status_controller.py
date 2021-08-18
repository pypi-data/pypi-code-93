from typing import List
from AsteriskRealtimeData.domain.queue_status.queue_status_search_criteria_vo import QueueStatusSearchCriteriaVo
from AsteriskRealtimeData.domain.queue_status.queue_status_update_vo import QueueStatusUpdateVo
from AsteriskRealtimeData.application.queue_status_service import QueueStatusService
from AsteriskRealtimeData.domain.queue_status.queue_status_vo import QueueStatusVo


class QueueStatusController:
    def create(self, queue_status_vo: QueueStatusVo) -> QueueStatusVo:
        return QueueStatusService().create_queue_status(queue_status_vo)

    def update(self, queue_status_update_vo: QueueStatusUpdateVo) -> QueueStatusVo:
        return QueueStatusService().update_queue_status(queue_status_update_vo)

    def get_all(self) -> List[QueueStatusVo]:
        queues_status = QueueStatusService().queue_status_list()
        result: list = []

        for queue_status in queues_status:
            result.append(queue_status)

        return result

    def get_by_status_code(self, status_code: str) -> QueueStatusVo:
        return QueueStatusService().get_queue_status(status_code)

    def get_by_search_criteria(self, search_criteria: QueueStatusSearchCriteriaVo) -> QueueStatusVo:
        return QueueStatusService().get_by_search_criteria(search_criteria)

    def delete_by_status_code(self, status_code: str) -> None:
        QueueStatusService().delete_queue_status(status_code)
