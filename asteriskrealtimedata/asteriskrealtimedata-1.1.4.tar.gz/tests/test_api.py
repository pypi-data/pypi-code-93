import unittest
from datetime import datetime
from unittest.mock import MagicMock
from typing import Final

from AsteriskRealtimeData.api import Api

from AsteriskRealtimeData.shared.errors.data_not_found_error import DataNotFound
from AsteriskRealtimeData.application.mascara_ipaddress_service import MascaraIpaddressService

from AsteriskRealtimeData.domain.queue_member.queue_member_search_criteria_vo import QueueMemberSearchCriteriaVo
from AsteriskRealtimeData.domain.queue_status.queue_status_search_criteria_vo import QueueStatusSearchCriteriaVo
from AsteriskRealtimeData.domain.peer.peer_search_criteria_vo import PeerSearchCriteriaVo
from AsteriskRealtimeData.domain.pause_reason.pause_reason_search_criteria_vo import PauseReasonSearchCriteriaVo
from AsteriskRealtimeData.domain.mascara_ipaddress.mascara_ipaddress_search_criteria_vo import (
    MascaraIpaddressSearchCriteriaVo,
)
from AsteriskRealtimeData.domain.call.call_search_criteria_vo import CallSerchCriteriaVo
from AsteriskRealtimeData.domain.call.call_update_vo import CallUpdateVo
from AsteriskRealtimeData.domain.queue_member.queue_member_update_vo import QueueMemberUpdateVo
from AsteriskRealtimeData.domain.queue_status.queue_status_update_vo import QueueStatusUpdateVo
from AsteriskRealtimeData.domain.peer.peer_update_vo import PeerUpdateVo
from AsteriskRealtimeData.domain.mascara_ipaddress.mascara_ipaddress_update_vo import MascaraIpaddressUpdateVo
from AsteriskRealtimeData.domain.pause_reason.pause_reason_update_vo import PauseReasonUpdateVo
from AsteriskRealtimeData.domain.call.call_vo import CallVo
from AsteriskRealtimeData.domain.mascara_ipaddress.mascara_ipaddress_vo import MascaraIpaddressVo
from AsteriskRealtimeData.domain.pause_reason.pause_reasons_vo import PauseReasonVo
from AsteriskRealtimeData.domain.peer.peer_vo import PeerVo
from AsteriskRealtimeData.domain.queue_member.queue_member_vo import QueueMemberVo
from AsteriskRealtimeData.domain.queue_status.queue_status_vo import QueueStatusVo


class TestAPI(unittest.TestCase):
    DATA_NO_FOUND: Final = "Data not found"
    DATETIME_FORMAT: Final = "%Y-%m-%d %H:%M:%S"

    def test_pause_reason(self):
        Api.PauseReason.create(PauseReasonVo(pause_code="1111", description="aaaaaa", paused=True))
        Api.PauseReason.create(PauseReasonVo(pause_code="2222", description="bbbbbb", paused=False))

        self.assertGreaterEqual(len(Api.PauseReason.get_all()), 2)
        self.assertDictEqual(
            Api.PauseReason.get_by_pause_code("2222").as_dict(),
            PauseReasonVo(pause_code="2222", description="bbbbbb", paused=False).as_dict(),
        )
        self.assertDictEqual(
            Api.PauseReason.get_by_pause_code("2222").as_dict(),
            Api.PauseReason.get_by_search_criteria(PauseReasonSearchCriteriaVo(pause_code="2222")).as_dict(),
        )

        Api.PauseReason.update(PauseReasonUpdateVo(pause_code="2222", description="A better description", paused=True))
        self.assertDictEqual(
            Api.PauseReason.get_by_pause_code("2222").as_dict(),
            PauseReasonVo(pause_code="2222", description="A better description", paused=True).as_dict(),
        )

        with self.assertRaises(DataNotFound) as context:
            Api.PauseReason.update(PauseReasonUpdateVo(pause_code="3333", description="Dont exists"))

        self.assertIsNone(Api.PauseReason.delete_by_pause_code("2222"))

        with self.assertRaises(DataNotFound) as context:
            Api.PauseReason.delete_by_pause_code("3333")
        self.assertTrue(self.DATA_NO_FOUND in str(context.exception))

        with self.assertRaises(DataNotFound) as context:
            Api.PauseReason.get_by_pause_code("3333")

        with self.assertRaises(DataNotFound) as context:
            Api.PauseReason.get_by_search_criteria(PauseReasonSearchCriteriaVo(description="not exist"))

    def test_mascara_ipaddress(self):
        actual_datetime = datetime.now().strftime(self.DATETIME_FORMAT)
        Api.MascaraIpaddress.create(MascaraIpaddressVo(ipaddress="1.1.1.1", lastconnection=actual_datetime))
        Api.MascaraIpaddress.create(MascaraIpaddressVo(ipaddress="2.2.2.2", lastconnection=actual_datetime))

        self.assertGreaterEqual(len(Api.MascaraIpaddress.get_all()), 2)

        self.assertDictEqual(
            Api.MascaraIpaddress.get_by_ipaddress("1.1.1.1").as_dict(),
            MascaraIpaddressVo(ipaddress="1.1.1.1", lastconnection=actual_datetime).as_dict(),
        )
        self.assertDictEqual(
            Api.MascaraIpaddress.get_by_search_criteria(
                MascaraIpaddressSearchCriteriaVo(ipaddress="2.2.2.2")
            ).as_dict(),
            MascaraIpaddressVo(ipaddress="2.2.2.2", lastconnection=actual_datetime).as_dict(),
        )

        new_lastconnection = datetime.now().strftime(self.DATETIME_FORMAT)
        Api.MascaraIpaddress.update(MascaraIpaddressUpdateVo(ipaddress="2.2.2.2", lastconnection=new_lastconnection))

        self.assertDictEqual(
            Api.MascaraIpaddress.get_by_ipaddress("2.2.2.2").as_dict(),
            MascaraIpaddressVo(ipaddress="2.2.2.2", lastconnection=new_lastconnection).as_dict(),
        )

        with self.assertRaises(DataNotFound) as context:
            Api.MascaraIpaddress.update(MascaraIpaddressUpdateVo(ipaddress="3.3.3.3", lastconnection=datetime.now()))
        self.assertTrue(self.DATA_NO_FOUND in str(context.exception))

        self.assertIsNone(Api.MascaraIpaddress.delete_by_ipaddress("1.1.1.1"))
        self.assertIsNone(Api.MascaraIpaddress.delete_by_ipaddress("2.2.2.2"))

        with self.assertRaises(DataNotFound) as context:
            Api.MascaraIpaddress.delete_by_ipaddress("2.2.2.2")
        self.assertTrue(self.DATA_NO_FOUND in str(context.exception))

        with self.assertRaises(DataNotFound) as context:
            Api.MascaraIpaddress.get_by_ipaddress("1.1.1.1")

        with self.assertRaises(DataNotFound) as context:
            Api.MascaraIpaddress.get_by_search_criteria(MascaraIpaddressSearchCriteriaVo(ipaddress="1.1.1.1"))

    def test_peer(self):
        Api.Peer.create(PeerVo(peer_name="SIP/100", peer_type="SIP", peer_ip_address="1.1.1.1"))
        Api.Peer.create(PeerVo(peer_name="SIP/200", peer_type="SIP", peer_ip_address="2.2.2.2"))

        self.assertGreaterEqual(len(Api.Peer.get_all()), 2)

        self.assertDictEqual(
            Api.Peer.get_by_peer("SIP/100").as_dict(),
            PeerVo(peer_name="SIP/100", peer_type="SIP", peer_ip_address="1.1.1.1").as_dict(),
        )
        self.assertDictEqual(
            Api.Peer.get_by_peer("SIP/200").as_dict(),
            PeerVo(peer_name="SIP/200", peer_type="SIP", peer_ip_address="2.2.2.2").as_dict(),
        )

        Api.Peer.update(PeerUpdateVo(peer_name="SIP/100", peer_ip_address="3.3.3.3"))

        self.assertDictEqual(
            Api.Peer.get_by_peer("SIP/100").as_dict(),
            PeerVo(peer_name="SIP/100", peer_type="SIP", peer_ip_address="3.3.3.3").as_dict(),
        )

        with self.assertRaises(DataNotFound) as context:
            Api.Peer.update(PeerUpdateVo(peer_name="SIP/300", peer_ip_address="3.3.3.3"))
        self.assertTrue(self.DATA_NO_FOUND in str(context.exception))

        self.assertIsNone(Api.Peer.delete_by_peer("SIP/100"))
        self.assertIsNone(Api.Peer.delete_by_peer("SIP/200"))

        with self.assertRaises(DataNotFound) as context:
            Api.Peer.delete_by_peer("SIP/100")
        self.assertTrue(self.DATA_NO_FOUND in str(context.exception))

        with self.assertRaises(DataNotFound) as context:
            Api.Peer.get_by_peer("SIP/100")

        with self.assertRaises(DataNotFound) as context:
            Api.Peer.get_by_search_criteria(PeerSearchCriteriaVo(peer_name="SIP/100"))

    def test_queue_status(self):
        Api.QueueStatus.create(QueueStatusVo(status_code="1000", description="Estado de la cola 1"))
        Api.QueueStatus.create(QueueStatusVo(status_code="2000", description="Estado de la cola 2"))

        self.assertGreaterEqual(len(Api.QueueStatus.get_all()), 2)

        self.assertDictEqual(
            Api.QueueStatus.get_by_status_code("1000").as_dict(),
            QueueStatusVo(status_code="1000", description="Estado de la cola 1").as_dict(),
        )
        self.assertDictEqual(
            Api.QueueStatus.get_by_status_code("2000").as_dict(),
            QueueStatusVo(status_code="2000", description="Estado de la cola 2").as_dict(),
        )

        Api.QueueStatus.update(QueueStatusUpdateVo(status_code="1000", description="Other description"))

        self.assertDictEqual(
            Api.QueueStatus.get_by_status_code("1000").as_dict(),
            QueueStatusVo(status_code="1000", description="Other description").as_dict(),
        )

        self.assertIsNone(Api.QueueStatus.delete_by_status_code("1000"))
        self.assertIsNone(Api.QueueStatus.delete_by_status_code("2000"))

        with self.assertRaises(DataNotFound) as context:
            Api.QueueStatus.delete_by_status_code("3000")
        self.assertTrue(self.DATA_NO_FOUND in str(context.exception))

        with self.assertRaises(DataNotFound) as context:
            Api.QueueStatus.get_by_status_code("1000")
        self.assertTrue(self.DATA_NO_FOUND in str(context.exception))

        with self.assertRaises(DataNotFound) as context:
            Api.QueueStatus.get_by_search_criteria(QueueStatusSearchCriteriaVo(status_code="1000"))
        self.assertTrue(self.DATA_NO_FOUND in str(context.exception))

    def test_queue_member(self):
        test_datetime = datetime.now().strftime(self.DATETIME_FORMAT)

        MascaraIpaddressService.get_mascara_ipaddress = MagicMock(
            return_value=MascaraIpaddressVo(ipaddress="1.1.1.1", lastconnection=datetime.now())
        )
        Api.QueueMember.create(
            QueueMemberVo(
                peer="SIP/1000",
                actual_status="1111",
                ipaddress="1.1.1.1",
                membername="Juca",
                last_status_datetime=test_datetime,
                is_queuemember=True,
            )
        )

        MascaraIpaddressService.get_mascara_ipaddress = MagicMock(
            return_value=MascaraIpaddressVo(ipaddress="3.3.3.3", lastconnection=datetime.now())
        )
        Api.QueueMember.create(
            QueueMemberVo(
                peer="SIP/2000",
                actual_status="2222",
                ipaddress="2.2.2.2",
                membername="Other",
                last_status_datetime=test_datetime,
                is_queuemember=False,
            )
        )

        self.assertGreaterEqual(len(Api.QueueMember.get_all()), 2)

        self.assertDictEqual(
            Api.QueueMember.get_by_peer("SIP/1000").as_dict(),
            QueueMemberVo(
                peer="SIP/1000",
                actual_status="1111",
                ipaddress="1.1.1.1",
                membername="Juca",
                last_status_datetime=test_datetime,
                is_queuemember=True,
            ).as_dict(),
        )

        self.assertDictEqual(
            Api.QueueMember.get_by_peer("SIP/2000").as_dict(),
            QueueMemberVo(
                peer="SIP/2000",
                actual_status="2222",
                ipaddress="2.2.2.2",
                membername="Other",
                last_status_datetime=test_datetime,
                is_queuemember=False,
            ).as_dict(),
        )

        Api.QueueMember.update(QueueMemberUpdateVo(peer="SIP/1000", ipaddress="3.3.3.3", membername="other name"))

        self.assertDictEqual(
            Api.QueueMember.get_by_peer("SIP/1000").as_dict(),
            QueueMemberVo(
                peer="SIP/1000",
                actual_status="1111",
                ipaddress="3.3.3.3",
                membername="other name",
                last_status_datetime=test_datetime,
                is_queuemember=True,
            ).as_dict(),
        )

        self.assertIsNone(Api.QueueMember.delete_by_peer("SIP/1000"))
        self.assertIsNone(Api.QueueMember.delete_by_peer("SIP/2000"))

        with self.assertRaises(DataNotFound) as context:
            Api.QueueMember.delete_by_peer("SIP/1000")
        self.assertTrue(self.DATA_NO_FOUND in str(context.exception))

        with self.assertRaises(DataNotFound) as context:
            Api.QueueMember.get_by_peer("SIP/1000")
        self.assertTrue(self.DATA_NO_FOUND in str(context.exception))

        with self.assertRaises(DataNotFound) as context:
            Api.QueueMember.get_by_search_criteria(QueueMemberSearchCriteriaVo(ipaddress="1.1.1.1"))
        self.assertTrue(self.DATA_NO_FOUND in str(context.exception))

    def test_call(self):
        test_datetime = datetime.now().strftime(self.DATETIME_FORMAT)

        Api.Call.create(
            CallVo(
                peer_name="SIP/100",
                client_id="1000",
                dialnumber="222222222",
                lastevent=test_datetime,
                track_id="1111",
                call_linkedid="1111",
                call_actor_address="actadd",
                event_name="evento",
                origin_channel="origchan",
                destination_channel="destchan",
                origin_number="1111111",
                destination_number="100",
            )
        )
        Api.Call.create(
            CallVo(
                peer_name="SIP/200",
                client_id="2000",
                dialnumber="333333333",
                lastevent=test_datetime,
                track_id="1111",
                call_linkedid="2222",
                call_actor_address="actadd",
                event_name="evento",
                origin_channel="origchan",
                destination_channel="destchan",
                origin_number="1111111",
                destination_number="100",
            )
        )

        self.assertDictEqual(
            Api.Call.get_by_call_linkedid("1111").as_dict(),
            CallVo(
                peer_name="SIP/100",
                client_id="1000",
                dialnumber="222222222",
                lastevent=test_datetime,
                track_id="1111",
                call_linkedid="1111",
                call_actor_address="actadd",
                event_name="evento",
                origin_channel="origchan",
                destination_channel="destchan",
                origin_number="1111111",
                destination_number="100",
            ).as_dict(),
        )

        self.assertDictEqual(
            Api.Call.get_by_call_linkedid("2222").as_dict(),
            CallVo(
                peer_name="SIP/200",
                client_id="2000",
                dialnumber="333333333",
                lastevent=test_datetime,
                track_id="1111",
                call_linkedid="2222",
                call_actor_address="actadd",
                event_name="evento",
                origin_channel="origchan",
                destination_channel="destchan",
                origin_number="1111111",
                destination_number="100",
            ).as_dict(),
        )

        self.assertGreaterEqual(len(Api.Call.get_all()), 2)

        Api.Call.update(CallUpdateVo(call_linkedid="1111", track_id="zzzzzzz", destination_channel="bbbbbbb"))

        self.assertDictEqual(
            Api.Call.get_by_call_linkedid("1111").as_dict(),
            CallVo(
                peer_name="SIP/100",
                client_id="1000",
                dialnumber="222222222",
                lastevent=test_datetime,
                track_id="zzzzzzz",
                call_linkedid="1111",
                call_actor_address="actadd",
                event_name="evento",
                origin_channel="origchan",
                destination_channel="bbbbbbb",
                origin_number="1111111",
                destination_number="100",
            ).as_dict(),
        )

        self.assertIsNone(Api.Call.delete_by_call_linkedid("1111"))
        self.assertIsNone(Api.Call.delete_by_call_linkedid("2222"))

        with self.assertRaises(DataNotFound) as context:
            Api.Call.delete_by_call_linkedid("1111")
        self.assertTrue(self.DATA_NO_FOUND in str(context.exception))

        with self.assertRaises(DataNotFound) as context:
            Api.Call.get_by_call_linkedid("1111")
        self.assertTrue(self.DATA_NO_FOUND in str(context.exception))

        with self.assertRaises(DataNotFound) as context:
            Api.Call.get_by_search_criteria(CallSerchCriteriaVo(peer_name="SIP/100"))
        self.assertTrue(self.DATA_NO_FOUND in str(context.exception))

