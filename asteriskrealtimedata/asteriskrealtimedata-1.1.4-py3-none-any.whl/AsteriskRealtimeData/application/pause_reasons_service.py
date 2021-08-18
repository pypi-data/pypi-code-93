from typing import List
from AsteriskRealtimeData.domain.pause_reason.pause_reason_search_criteria_vo import PauseReasonSearchCriteriaVo
from AsteriskRealtimeData.domain.pause_reason.pause_reason_update_vo import PauseReasonUpdateVo
from antidote import Provide, inject
from antidote.core.injection import F
from AsteriskRealtimeData.application.pause_reason_repository import PauseReasonRepository
from AsteriskRealtimeData.domain.pause_reason.pause_reason import PauseReason
from AsteriskRealtimeData.domain.pause_reason.pause_reasons_vo import PauseReasonVo


class PauseReasonService:
    @inject
    def create_pause_reason(
        self, pause_reason_vo: PauseReasonVo, repository: Provide[PauseReasonRepository]
    ) -> PauseReasonVo:

        pause_reason = PauseReason(
            pause_code=pause_reason_vo.pause_code,
            description=pause_reason_vo.description,
            paused=pause_reason_vo.paused,
        )

        repository.save(pause_reason, {"pause_code": pause_reason_vo.pause_code})

        return PauseReasonVo(
            pause_code=pause_reason_vo.pause_code,
            description=pause_reason_vo.description,
            paused=pause_reason_vo.paused,
        )

    @inject
    def update_pause_reason(
        self, pause_reason_update_vo: PauseReasonUpdateVo, repository: Provide[PauseReasonRepository]
    ) -> PauseReasonVo:

        repository.update(pause_reason_update_vo)

        pause_reason_dict = repository.get_by_criteria(pause_reason_update_vo.get_key_field())

        return PauseReasonVo(
            pause_code=pause_reason_dict["pause_code"],
            description=pause_reason_dict["description"],
            paused=pause_reason_dict["paused"],
        )

    @inject()
    def pause_reason_list(self, repository: Provide[PauseReasonRepository]) -> List[PauseReasonVo]:
        result: list = []
        for document in repository.list():
            result.append(
                PauseReasonVo(
                    pause_code=document["pause_code"], description=document["description"], paused=document["paused"],
                )
            )
        return result

    @inject
    def get_pause_reason(self, pause_code: str, repository: Provide[PauseReasonRepository]) -> PauseReasonVo:
        pause_reason = repository.get_by_criteria({"pause_code": pause_code})
        return PauseReasonVo(
            pause_code=pause_reason["pause_code"],
            description=pause_reason["description"],
            paused=pause_reason["paused"],
        )

    @inject
    def get_by_search_criteria(
        self, search_criteria: PauseReasonSearchCriteriaVo, repository: Provide[PauseReasonRepository]
    ) -> PauseReasonVo:
        pause_reason = repository.get_by_criteria(search_criteria.as_dict())
        return PauseReasonVo(
            pause_code=pause_reason["pause_code"],
            description=pause_reason["description"],
            paused=pause_reason["paused"],
        )

    @inject
    def delete_pause_reason(self, pause_code: str, repository: Provide[PauseReasonRepository]) -> None:
        repository.delete_by_criteria({"pause_code": pause_code})
