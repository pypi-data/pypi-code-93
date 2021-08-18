from typing import List
from AsteriskRealtimeData.domain.queue_member.queue_member_search_criteria_vo import QueueMemberSearchCriteriaVo
from AsteriskRealtimeData.domain.queue_member.queue_member_update_vo import QueueMemberUpdateVo
from AsteriskRealtimeData.application.queue_member_service import QueueMemberService
from AsteriskRealtimeData.domain.queue_member.queue_member_vo import QueueMemberVo


class QueueMemberController:
    def create(self, queue_member_vo: QueueMemberVo) -> QueueMemberVo:
        return QueueMemberService().create_queue_member(queue_member_vo)

    def update(self, queue_member_update_vo: QueueMemberUpdateVo) -> QueueMemberVo:
        return QueueMemberService().update_queue_member(queue_member_update_vo)

    def get_all(self) -> List[QueueMemberVo]:
        queue_members = QueueMemberService().queue_member_list()
        result: list = []

        for queue_member in queue_members:
            result.append(queue_member)

        return result

    def get_by_peer(self, peer: str) -> QueueMemberVo:
        return QueueMemberService().get_queue_member(peer)

    def get_by_search_criteria(self, search_criteria: QueueMemberSearchCriteriaVo) -> QueueMemberVo:
        return QueueMemberService().get_by_search_criteria(search_criteria)

    def delete_by_peer(self, peer: str) -> None:
        QueueMemberService().delete_queue_member(peer)
