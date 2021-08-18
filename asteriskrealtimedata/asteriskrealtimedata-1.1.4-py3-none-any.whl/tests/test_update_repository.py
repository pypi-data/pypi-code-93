import unittest
from datetime import datetime
from time import sleep
from AsteriskRealtimeData.api import Api
from AsteriskRealtimeData.domain.mascara_ipaddress.mascara_ipaddress_update_vo import MascaraIpaddressUpdateVo
from AsteriskRealtimeData.domain.mascara_ipaddress.mascara_ipaddress_vo import MascaraIpaddressVo
from AsteriskRealtimeData.domain.pause_reason.pause_reason_update_vo import PauseReasonUpdateVo
from AsteriskRealtimeData.domain.pause_reason.pause_reasons_vo import PauseReasonVo


class TestUpdateRepository(unittest.TestCase):
    def test_update_pause_reason(self):
        Api.PauseReason.create(PauseReasonVo(pause_code="000000", description="Must be updated", paused=False))
        Api.PauseReason.update(PauseReasonUpdateVo(pause_code="000000", description="Updated"))

        pause_reason = Api.PauseReason.get_by_pause_code("000000")

        self.assertDictEqual(pause_reason, {"pause_code": "000000", "description": "Updated", "paused": False})

        Api.PauseReason.update(PauseReasonUpdateVo(pause_code="000000", paused=True))

        pause_reason = Api.PauseReason.get_by_pause_code("000000")

        self.assertDictEqual(pause_reason, {"pause_code": "000000", "description": "Updated", "paused": True})

        Api.PauseReason.delete_by_pause_code("000000")

    def test_update_mascara_ipaddress(self):
        actual_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Api.MascaraIpaddress.create(MascaraIpaddressVo(ipaddress="0.0.0.0", lastconnection=datetime.now()))

        Api.MascaraIpaddress.update(MascaraIpaddressUpdateVo(ipaddress="0.0.0.0", lastconnection=actual_datetime))

        mascara_ipaddress = Api.MascaraIpaddress.get_by_ipaddress("0.0.0.0")

        self.assertDictEqual(mascara_ipaddress, {"ipaddress": "0.0.0.0", "lastconnection": actual_datetime})

        Api.MascaraIpaddress.delete_by_ipaddress("0.0.0.0")
