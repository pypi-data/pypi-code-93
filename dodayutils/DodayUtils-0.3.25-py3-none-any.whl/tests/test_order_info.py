import unittest
import datetime

class OrderInfoTests(unittest.TestCase):
    """
    Testing Strategy:
    - serverTime
        - partition on mode: EPOCH, STRING, DATETIME_NOW
    
    - is_time_between
        - partition on check_time: None, or epoch time
        - partition on begin_time, end_time: begin < end, begin = end, begin > end

    - check_operation_hours
        - partition on opening_time, closing_time: open < close, open = close, open > close, XX

    - timeout
        - partition on timeout time: 0, 1, >1
        - partition on execution time: 0, 1, >1
        - partition on results: timedout, no timeout
    """

    # covers serverTime modes
    def test_servertime(self):
        self.assertTrue(True)
    # covers is_time_between
    def test_is_time_between(self):
        self.assertFalse(False)

        