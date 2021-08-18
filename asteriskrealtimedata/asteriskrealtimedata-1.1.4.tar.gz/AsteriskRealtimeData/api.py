from typing import List
from AsteriskRealtimeData.domain.call.call_update_vo import CallUpdateVo
from AsteriskRealtimeData.domain.call.call_search_criteria_vo import CallSerchCriteriaVo
from AsteriskRealtimeData.domain.call.call_vo import CallVo
from AsteriskRealtimeData.domain.mascara_ipaddress.mascara_ipaddress_update_vo import MascaraIpaddressUpdateVo
from AsteriskRealtimeData.domain.mascara_ipaddress.mascara_ipaddress_search_criteria_vo import (
    MascaraIpaddressSearchCriteriaVo,
)
from AsteriskRealtimeData.domain.mascara_ipaddress.mascara_ipaddress_vo import MascaraIpaddressVo
from AsteriskRealtimeData.domain.pause_reason.pause_reason_update_vo import PauseReasonUpdateVo
from AsteriskRealtimeData.domain.pause_reason.pause_reason_search_criteria_vo import PauseReasonSearchCriteriaVo
from AsteriskRealtimeData.domain.pause_reason.pause_reasons_vo import PauseReasonVo
from AsteriskRealtimeData.domain.peer.peer_update_vo import PeerUpdateVo
from AsteriskRealtimeData.domain.peer.peer_search_criteria_vo import PeerSearchCriteriaVo
from AsteriskRealtimeData.domain.peer.peer_vo import PeerVo
from AsteriskRealtimeData.domain.queue_member.queue_member_vo import QueueMemberVo
from AsteriskRealtimeData.domain.queue_member.queue_member_search_criteria_vo import QueueMemberSearchCriteriaVo
from AsteriskRealtimeData.domain.queue_status.queue_status_update_vo import QueueStatusUpdateVo
from AsteriskRealtimeData.domain.queue_status.queue_status_search_criteria_vo import QueueStatusSearchCriteriaVo
from AsteriskRealtimeData.domain.queue_status.queue_status_vo import QueueStatusVo

from AsteriskRealtimeData.infrastructure.api.pause_reason_controller import PauseReasonController
from AsteriskRealtimeData.infrastructure.api.mascara_ipaddress_controller import MascaraIpaddressController
from AsteriskRealtimeData.infrastructure.api.queue_member_controller import QueueMemberController
from AsteriskRealtimeData.infrastructure.api.peer_controller import PeerController
from AsteriskRealtimeData.infrastructure.api.queue_status_controller import QueueStatusController
from AsteriskRealtimeData.infrastructure.api.call_controller import CallController


class Api:
    class Call:
        @staticmethod
        def create(call: CallVo) -> CallVo:
            return CallController().create(call)

        @staticmethod
        def update(call_update_vo: CallUpdateVo) -> CallVo:
            return CallController().update(call_update_vo)

        @staticmethod
        def get_all() -> List[CallVo]:
            return CallController().get_all()

        @staticmethod
        def get_by_call_linkedid(call_linkedid: str) -> CallVo:
            return CallController().get_by_call_linkedid(call_linkedid)

        @staticmethod
        def get_by_search_criteria(search_criteria: CallSerchCriteriaVo) -> CallVo:
            return CallController().get_by_search_criteria(search_criteria)

        @staticmethod
        def delete_by_call_linkedid(call_linkedid: str) -> None:
            CallController().delete_by_call_linkedid(call_linkedid)

    class MascaraIpaddress:
        @staticmethod
        def create(mascara_ipaddress: MascaraIpaddressVo) -> MascaraIpaddressVo:
            return MascaraIpaddressController().create(mascara_ipaddress)

        @staticmethod
        def update(mascara_ipaddress: MascaraIpaddressUpdateVo) -> MascaraIpaddressVo:
            return MascaraIpaddressController().update(mascara_ipaddress)

        @staticmethod
        def get_all() -> List[MascaraIpaddressVo]:
            return MascaraIpaddressController().get_all()

        @staticmethod
        def get_by_ipaddress(mascara_ipaddress: str) -> MascaraIpaddressVo:
            return MascaraIpaddressController().get_by_ipaddress(mascara_ipaddress)

        @staticmethod
        def get_by_search_criteria(search_criteria: MascaraIpaddressSearchCriteriaVo) -> MascaraIpaddressVo:
            return MascaraIpaddressController().get_by_search_criteria(search_criteria)

        @staticmethod
        def delete_by_ipaddress(mascara_ipaddress: str) -> None:
            MascaraIpaddressController().delete_by_ipaddress(mascara_ipaddress)

    class PauseReason:
        @staticmethod
        def create(pause_reason: PauseReasonVo) -> PauseReasonVo:
            return PauseReasonController().create(pause_reason)

        @staticmethod
        def update(pause_reason: PauseReasonUpdateVo) -> PauseReasonVo:
            return PauseReasonController().update(pause_reason)

        @staticmethod
        def get_all() -> List[PauseReasonVo]:
            return PauseReasonController().get_all()

        @staticmethod
        def get_by_pause_code(pause_code: str) -> PauseReasonVo:
            return PauseReasonController().get_by_pause_code(pause_code)

        @staticmethod
        def get_by_search_criteria(search_criteria: PauseReasonSearchCriteriaVo) -> PauseReasonVo:
            return PauseReasonController().get_by_search_criteria(search_criteria)

        @staticmethod
        def delete_by_pause_code(pause_code: str) -> None:
            PauseReasonController().delete_by_pause_code(pause_code)

    class Peer:
        @staticmethod
        def create(peer: PeerVo) -> PeerVo:
            return PeerController().create(peer)

        @staticmethod
        def update(peer: PeerUpdateVo) -> PeerVo:
            return PeerController().update(peer)

        @staticmethod
        def get_all() -> List[PeerVo]:
            return PeerController().get_all()

        @staticmethod
        def get_by_peer(peer: str) -> PeerVo:
            return PeerController().get_by_peer(peer)

        @staticmethod
        def get_by_search_criteria(search_criteria: PeerSearchCriteriaVo) -> PeerVo:
            return PeerController().get_by_search_criteria(search_criteria)

        @staticmethod
        def delete_by_peer(peer: str) -> None:
            PeerController().delete_by_peer(peer)

    class QueueMember:
        @staticmethod
        def create(queue_member: QueueMemberVo) -> QueueMemberVo:
            return QueueMemberController().create(queue_member)

        @staticmethod
        def update(queue_member_update_vo: QueueStatusUpdateVo) -> QueueMemberVo:
            return QueueMemberController().update(queue_member_update_vo)

        @staticmethod
        def get_all() -> List[QueueMemberVo]:
            return QueueMemberController().get_all()

        @staticmethod
        def get_by_peer(peer: str) -> QueueMemberVo:
            return QueueMemberController().get_by_peer(peer)

        @staticmethod
        def get_by_search_criteria(search_criteria: QueueMemberSearchCriteriaVo) -> QueueMemberVo:
            return QueueMemberController().get_by_search_criteria(search_criteria)

        @staticmethod
        def delete_by_peer(peer: str) -> None:
            QueueMemberController().delete_by_peer(peer)

    class QueueStatus:
        @staticmethod
        def create(queue_status: QueueStatusVo) -> QueueStatusVo:
            return QueueStatusController().create(queue_status)

        def update(queue_status_update_vo: QueueStatusUpdateVo) -> QueueStatusVo:
            return QueueStatusController().update(queue_status_update_vo)

        @staticmethod
        def get_all() -> List[QueueStatusVo]:
            return QueueStatusController().get_all()

        @staticmethod
        def get_by_status_code(status_code: str) -> QueueStatusVo:
            return QueueStatusController().get_by_status_code(status_code)

        @staticmethod
        def get_by_search_criteria(search_criteria: QueueStatusSearchCriteriaVo) -> QueueStatusVo:
            return QueueStatusController().get_by_search_criteria(search_criteria)

        @staticmethod
        def delete_by_status_code(status_code: str) -> None:
            QueueStatusController().delete_by_status_code(status_code)

