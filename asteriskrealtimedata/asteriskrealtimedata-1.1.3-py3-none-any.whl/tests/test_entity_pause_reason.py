import unittest
from AsteriskRealtimeData.domain.pause_reason.pause_reason import PauseReason
from uuid import uuid4


class TestPauseReason(unittest.TestCase):
    def test_create_pause_reason(self):
        pause_reason = PauseReason(pause_code="0000001", description="Testing")
        # print(str(pause_reason))
        print(pause_reason.description)

        # print(pause_reason.get_table_name())
        # pause_reason = PauseReason("100000", "testing")
        # self.assertEqual(pause_reason.get_pause_code(), "100000")
