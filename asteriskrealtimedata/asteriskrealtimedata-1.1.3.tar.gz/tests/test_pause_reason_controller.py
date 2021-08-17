from AsteriskRealtimeData.domain.pause_reason.pause_reasons_vo import PauseReasonVo
import unittest
from AsteriskRealtimeData.infrastructure.api.pause_reason_controller import PauseReasonController


class TestPauseReasonController(unittest.TestCase):
    def test_create_pause_reason_from_controller(self):

        pause_reason_controller = PauseReasonController().create(
            PauseReasonVo(pause_code="100001", description="testing", paused=True)
        )
        print(pause_reason_controller)

