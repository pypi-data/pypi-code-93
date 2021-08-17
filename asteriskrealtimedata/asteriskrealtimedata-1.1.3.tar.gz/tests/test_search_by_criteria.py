import unittest

from AsteriskRealtimeData.domain.call.call_search_criteria_vo import CallSerchCriteriaVo


class TestUpdateVo(unittest.TestCase):
    def test_call_search_by_criteria_vo(self):
        search_one_term = CallSerchCriteriaVo(peer_name="SIP/100", origin_channel="123")
        print(search_one_term.as_dict())
