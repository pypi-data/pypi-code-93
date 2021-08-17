from datetime import datetime
import unittest
from AsteriskRealtimeData.domain.call.call_update_vo import CallUpdateVo
from AsteriskRealtimeData.domain.mascara_ipaddress.mascara_ipaddress_update_vo import MascaraIpaddressUpdateVo
from AsteriskRealtimeData.domain.pause_reason.pause_reason_update_vo import PauseReasonUpdateVo
from AsteriskRealtimeData.domain.queue_member.queue_member_update_vo import QueueMemberUpdateVo
from AsteriskRealtimeData.domain.queue_status.queue_status_update_vo import QueueStatusUpdateVo


class TestUpdateVo(unittest.TestCase):
    def test_update_queue_member(self):
        qm = QueueMemberUpdateVo(peer="SIP/100", membername="Pruebas", actual_status="100001")
        self.assertDictEqual(qm.get_update_fields(), {"actual_status": "100001", "membername": "Pruebas"})
        self.assertDictEqual(qm.get_key_field(), {"peer": "SIP/100"})

    def test_update_queue_member_different_key(self):
        qm = QueueMemberUpdateVo(peer="SIP/100", membername="Pruebas", actual_status="100001")
        qm.set_key_field_name("membername")
        self.assertDictEqual(qm.get_update_fields(), {"peer": "SIP/100", "actual_status": "100001"})
        self.assertDictEqual(qm.get_key_field(), {"membername": "Pruebas"})

    def test_update_call(self):
        qm = CallUpdateVo(call_linkedid="1111", lastevent="testing", destination_channel="SIP/111-1234")
        self.assertDictEqual(qm.get_update_fields(), {"lastevent": "testing", "destination_channel": "SIP/111-1234"})
        self.assertDictEqual(qm.get_key_field(), {"call_linkedid": "1111"})

    def test_update_call_different_key(self):
        qm = CallUpdateVo(call_linkedid="1111", lastevent="testing", destination_channel="SIP/111-1234")
        qm.set_key_field_name("destination_channel")
        self.assertDictEqual(qm.get_update_fields(), {"lastevent": "testing", "call_linkedid": "1111"})
        self.assertDictEqual(qm.get_key_field(), {"destination_channel": "SIP/111-1234"})

    def test_update_mascara_ipaddress(self):
        lastconnection_datetime = datetime.now()
        qm = MascaraIpaddressUpdateVo(ipaddress="2.2.2.2", lastconnection=lastconnection_datetime)
        self.assertDictEqual(qm.get_update_fields(), {"lastconnection": lastconnection_datetime})
        self.assertDictEqual(qm.get_key_field(), {"ipaddress": "2.2.2.2"})

    def test_update_mascara_ipaddress_different_key(self):
        lastconnection_datetime = datetime.now()
        qm = MascaraIpaddressUpdateVo(ipaddress="2.2.2.2", lastconnection=lastconnection_datetime)
        qm.set_key_field_name("lastconnection")
        self.assertDictEqual(qm.get_update_fields(), {"ipaddress": "2.2.2.2"})
        self.assertDictEqual(qm.get_key_field(), {"lastconnection": lastconnection_datetime})

    def test_update_pause_reason(self):
        qm = PauseReasonUpdateVo(pause_code="000000", paused=True)
        self.assertDictEqual(qm.get_update_fields(), {"paused": True})
        self.assertDictEqual(qm.get_key_field(), {"pause_code": "000000"})

    def test_update_pause_reason_different_key(self):
        qm = PauseReasonUpdateVo(pause_code="000000", paused=True)
        qm.set_key_field_name("paused")
        self.assertDictEqual(qm.get_update_fields(), {"pause_code": "000000"})
        self.assertDictEqual(qm.get_key_field(), {"paused": True})

    def test_update_queue_status(self):
        qm = QueueStatusUpdateVo(status_code="1", description="test")
        self.assertDictEqual(qm.get_update_fields(), {"description": "test"})
        self.assertDictEqual(qm.get_key_field(), {"status_code": "1"})

    def test_update_queue_status_different_key(self):
        qm = QueueStatusUpdateVo(status_code="1", description="test")
        qm.set_key_field_name("description")
        self.assertDictEqual(qm.get_update_fields(), {"status_code": "1"})
        self.assertDictEqual(qm.get_key_field(), {"description": "test"})
