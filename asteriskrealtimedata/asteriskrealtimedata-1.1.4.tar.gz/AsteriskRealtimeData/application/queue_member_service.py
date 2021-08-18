from typing import List
from AsteriskRealtimeData.domain.queue_member.queue_member_search_criteria_vo import QueueMemberSearchCriteriaVo
from AsteriskRealtimeData.domain.queue_member.queue_member_update_vo import QueueMemberUpdateVo
from AsteriskRealtimeData.application.queue_member_repository import QueueMemberRepository
from antidote import inject, Provide
from AsteriskRealtimeData.domain.queue_member.queue_member import QueueMember
from AsteriskRealtimeData.domain.queue_member.queue_member_vo import QueueMemberVo
from AsteriskRealtimeData.application.mascara_ipaddress_service import MascaraIpaddressService


class QueueMemberService:
    @inject
    def create_queue_member(
        self, queue_member_vo: QueueMemberVo, repository: Provide[QueueMemberRepository]
    ) -> QueueMemberVo:

        mascara_ipaddress = MascaraIpaddressService().get_mascara_ipaddress(queue_member_vo.ipaddress)

        is_queue_member = mascara_ipaddress.ipaddress == queue_member_vo.ipaddress

        queue_member = QueueMember(
            peer=queue_member_vo.peer,
            actual_status=queue_member_vo.actual_status,
            ipaddress=queue_member_vo.ipaddress,
            membername=queue_member_vo.membername,
            last_status_datetime=queue_member_vo.last_status_datetime,
            is_queuemember=is_queue_member,
        )

        repository.save(queue_member, {"peer": queue_member_vo.peer})

        return QueueMemberVo(
            peer=queue_member_vo.peer,
            actual_status=queue_member_vo.actual_status,
            ipaddress=queue_member_vo.ipaddress,
            membername=queue_member_vo.membername,
            last_status_datetime=queue_member_vo.last_status_datetime,
            is_queuemember=is_queue_member,
        )

    @inject
    def update_queue_member(
        self, queue_member_update_vo: QueueMemberUpdateVo, repository: Provide[QueueMemberRepository]
    ) -> QueueMemberVo:
        repository.update(queue_member_update_vo)

        queue_member_dict = repository.get_by_criteria(queue_member_update_vo.get_key_field())

        return QueueMemberVo(
            peer=queue_member_dict["peer"],
            actual_status=queue_member_dict["actual_status"],
            ipaddress=queue_member_dict["ipaddress"],
            membername=queue_member_dict["membername"],
            last_status_datetime=queue_member_dict["last_status_datetime"],
            is_queuemember=queue_member_dict["is_queuemember"],
        )

    @inject()
    def queue_member_list(self, repository: Provide[QueueMemberRepository]) -> List[QueueMemberVo]:
        result: list = []
        for document in repository.list():
            result.append(
                QueueMemberVo(
                    peer=document["peer"],
                    actual_status=document["actual_status"],
                    ipaddress=document["ipaddress"],
                    membername=document["membername"],
                    last_status_datetime=document["last_status_datetime"],
                    is_queuemember=document["is_queuemember"],
                )
            )
        return result

    @inject
    def get_queue_member(self, peer: str, repository: Provide[QueueMemberRepository]) -> QueueMemberVo:
        queue_member = repository.get_by_criteria({"peer": peer})
        return QueueMemberVo(
            peer=queue_member["peer"],
            actual_status=queue_member["actual_status"],
            ipaddress=queue_member["ipaddress"],
            membername=queue_member["membername"],
            last_status_datetime=queue_member["last_status_datetime"],
            is_queuemember=queue_member["is_queuemember"],
        )

    @inject
    def get_by_search_criteria(
        self, search_criteria: QueueMemberSearchCriteriaVo, repository: Provide[QueueMemberRepository]
    ) -> QueueMemberVo:
        queue_member = repository.get_by_criteria(search_criteria.as_dict())
        return QueueMemberVo(
            peer=queue_member["peer"],
            actual_status=queue_member["actual_status"],
            ipaddress=queue_member["ipaddress"],
            membername=queue_member["membername"],
            last_status_datetime=queue_member["last_status_datetime"],
            is_queuemember=queue_member["is_queuemember"],
        )

    @inject
    def delete_queue_member(self, peer: str, repository: Provide[QueueMemberRepository]) -> None:
        repository.delete_by_criteria({"peer": peer})
