from typing import List
from AsteriskRealtimeData.domain.queue_status.queue_status_search_criteria_vo import QueueStatusSearchCriteriaVo
from AsteriskRealtimeData.domain.queue_status.queue_status_update_vo import QueueStatusUpdateVo
from antidote import inject, Provide

from AsteriskRealtimeData.application.queue_status_repository import QueueStatusRepository
from AsteriskRealtimeData.domain.queue_status.queue_status import QueueStatus
from AsteriskRealtimeData.domain.queue_status.queue_status_vo import QueueStatusVo


class QueueStatusService:
    @inject
    def create_queue_status(
        self, queue_status_vo: QueueStatusVo, repository: Provide[QueueStatusRepository]
    ) -> QueueStatusVo:

        repository.save(queue_status_vo, {"status_code": queue_status_vo.status_code})

        return QueueStatusVo(status_code=queue_status_vo.status_code, description=queue_status_vo.description,)

    @inject
    def update_queue_status(
        self, queue_status_update_vo: QueueStatusUpdateVo, repository: Provide[QueueStatusRepository]
    ) -> QueueStatusVo:
        repository.update(queue_status_update_vo)

        queue_status_dict = repository.get_by_criteria(queue_status_update_vo.get_key_field())

        return QueueStatusVo(status_code=queue_status_dict["status_code"], description=queue_status_dict["description"])

    @inject()
    def queue_status_list(self, repository: Provide[QueueStatusRepository]) -> List[QueueStatusVo]:
        result: list = []
        for document in repository.list():
            result.append(QueueStatusVo(status_code=document["status_code"], description=document["description"],))
        return result

    @inject
    def get_queue_status(self, status_code: str, repository: Provide[QueueStatusRepository]) -> QueueStatusVo:
        queue_status = repository.get_by_criteria({"status_code": status_code})
        return QueueStatusVo(status_code=queue_status["status_code"], description=queue_status["description"],)

    @inject
    def get_by_search_criteria(
        self, search_criteria: QueueStatusSearchCriteriaVo, repository: Provide[QueueStatusRepository]
    ) -> QueueStatusVo:
        queue_status = repository.get_by_criteria(search_criteria.as_dict())
        return QueueStatusVo(status_code=queue_status["status_code"], description=queue_status["description"],)

    @inject
    def delete_queue_status(self, status_code: str, repository: Provide[QueueStatusRepository]) -> None:
        repository.delete_by_criteria({"status_code": status_code})
