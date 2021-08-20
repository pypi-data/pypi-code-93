import time
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.transport.timer import RepeatedTimer


class RepeatedTimerTest(TestCase):
    def setUp(self):
        self.function_mock = mock.Mock()
        self.timer = RepeatedTimer(0.1, self.function_mock)

    def shutDown(self):
        self.timer.stop()

    def test_timer(self):
        self.timer.start()
        time.sleep(0.3)

        assert self.function_mock.called
        assert self.function_mock.call_count >= 2
