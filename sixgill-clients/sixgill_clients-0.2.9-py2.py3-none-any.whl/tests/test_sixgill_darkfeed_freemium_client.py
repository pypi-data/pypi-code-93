from mock import patch
import logging

from tests.test_sixgill_base_client import TestSixgillBaseClient
from sixgill.sixgill_feed_client import SixgillFeedClient
from sixgill.sixgill_constants import FeedStream


class TestSixgillDarkFeedClient(TestSixgillBaseClient):

    def setUp(self):
        super(TestSixgillDarkFeedClient, self).setUp()
        self.sixgill_darkfeed_freemium_client = SixgillFeedClient('client_id', 'secret', 'random',
                                                                  FeedStream.DARKFEED_FREEMIUM,
                                                                  logging.getLogger("test"), bulk_size=7)

    def test_get_indicators(self):
        with patch('requests.sessions.Session.send', new=self.mocked_request):
            indicators = []
            for indicator in self.sixgill_darkfeed_freemium_client.get_indicator():
                indicators.append(indicator)

        expected_output = [{'created': '2020-01-09T07:31:10.991Z',
                            'description': 'Shell access to this domain is being sold on dark web markets',
                            'id': 'indicator--<some-id>',
                            'kill_chain_phases': [{'kill_chain_name': 'some-name',
                                                   'phase_name': 'abc'}],
                            'labels': ['compromised', 'shell', 'webshell'], 'lang': 'en',
                            'modified': '2020-01-09T07:31:10.991Z', 'object_marking_refs': [
                                'marking-definition--41eaaf7c-0bc0-4c56-abdf-d89a7f096ac4',
                                'marking-definition--f88d31f6-486f-44da-b317-01333bde0b82'],
                            'pattern': "[domain-name:value = 'http://website-test.com']",
                            'sixgill_actor': 'abc', 'sixgill_confidence': 90,
                            'sixgill_feedid': 'darkfeed_1', 'sixgill_feedname': 'compromised_sites',
                            'sixgill_postid': '5e3930cb109942847a0af98934f5ed12f094138a',
                            'sixgill_posttitle': 'name Test       http://website-test.com',
                            'sixgill_severity': 70, 'sixgill_source': 'market_magbo',
                            'spec_version': '2.0', 'type': 'indicator',
                            'valid_from': '2019-12-05T17:15:40Z'},
                           {'created': '2020-01-09T07:31:11.007Z',
                            'description': 'Shell access to this domain is being sold on dark web markets',
                            'id': 'indicator--851269aa-f9f9-4375-a5af-3fbe35729fb7', 'kill_chain_phases': [
                               {'kill_chain_name': 'some-name', 'phase_name': 'abc'}],
                            'labels': ['compromised', 'shell', 'webshell'], 'lang': 'ru',
                            'modified': '2020-01-09T07:31:11.007Z',
                            'object_marking_refs': ['marking-definition--41eaaf7c-0bc0-4c56-abdf-d89a7f096ac4',
                                                    'marking-definition--f88d31f6-486f-44da-b317-01333bde0b82'],
                            'pattern': "[domain-name:value = 'https://someweb.no']", 'sixgill_actor': 'abc',
                            'sixgill_confidence': 90, 'sixgill_feedid': 'darkfeed_1',
                            'sixgill_feedname': 'compromised_sites',
                            'sixgill_postid': '5cd7f37cffa1687f271750196fe616f1179d2d04',
                            'sixgill_posttitle': 'https://someweb.no',
                            'sixgill_severity': 70, 'sixgill_source': 'market_magbo', 'spec_version': '2.0',
                            'type': 'indicator',
                            'valid_from': '2019-12-05T19:18:36Z'},
                           {'created': '2020-01-09T07:31:10.986Z',
                            'description': 'Shell access to this domain is being sold on dark web markets',
                            'id': 'indicator--f050b41e-0349-4545-8fc1-8cc33016bae4',
                            'kill_chain_phases': [
                                {
                                    'kill_chain_name': 'some-name',
                                    'phase_name': 'abc'}],
                            'labels': ['compromised', 'shell', 'webshell'],
                            'lang': 'en',
                            'modified': '2020-01-09T07:31:10.986Z',
                            'object_marking_refs': [
                                'marking-definition--41eaaf7c-0bc0-4c56-abdf-d89a7f096ac4',
                                'marking-definition--f88d31f6-486f-44da-b317-01333bde0b82'],
                            'pattern': "[domain-name:value = 'https://somewebsite.co.uk']",
                            'sixgill_actor': 'abc',
                            'sixgill_confidence': 90,
                            'sixgill_feedid': 'darkfeed_1',
                            'sixgill_feedname': 'compromised_sites',
                            'sixgill_postid': '9d9d1dc99040d1feb63f2b3a9747bf6e862cafa8',
                            'sixgill_posttitle': '       https://somewebsite.co.uk',
                            'sixgill_severity': 70,
                            'sixgill_source': 'market_magbo',
                            'spec_version': '2.0', 'type': 'indicator',
                            'valid_from': '2019-12-05T18:00:47Z'},
                           {'created': '2020-01-09T07:31:11.037Z',
                            'description': 'Shell access to this domain is being sold on dark web markets',
                            'id': 'indicator--7aaa8d80-ff19-47bc-ad8c-f6a94c4f88fd', 'kill_chain_phases': [
                               {'kill_chain_name': 'some-name', 'phase_name': 'abc'}],
                            'labels': ['compromised', 'shell', 'webshell'], 'lang': 'en',
                            'modified': '2020-01-09T07:31:11.037Z',
                            'object_marking_refs': ['marking-definition--41eaaf7c-0bc0-4c56-abdf-d89a7f096ac4',
                                                    'marking-definition--f88d31f6-486f-44da-b317-01333bde0b82'],
                            'pattern': "[domain-name:value = 'http://somewebsite.com']", 'sixgill_actor': 'abc',
                            'sixgill_confidence': 90, 'sixgill_feedid': 'darkfeed_1',
                            'sixgill_feedname': 'compromised_sites',
                            'sixgill_postid': '86dbf0af5ba1aef05e2b60267043c55327a897dd',
                            'sixgill_posttitle': 'http://somewebsite.com',
                            'sixgill_severity': 70, 'sixgill_source': 'market_magbo', 'spec_version': '2.0',
                            'type': 'indicator',
                            'valid_from': '2019-12-06T14:26:35Z'},
                           {'created': '2020-01-09T07:31:11.167Z',
                            'description': 'Shell access to this domain is being sold on dark web markets',
                            'id': 'indicator--167a2ae5-caa6-45d7-935f-b529f4ec2c01',
                            'kill_chain_phases': [
                                {
                                    'kill_chain_name': 'some-name',
                                    'phase_name': 'abc'}],
                            'labels': ['compromised', 'shell', 'webshell'],
                            'lang': 'un',
                            'modified': '2020-01-09T07:31:11.167Z',
                            'object_marking_refs': [
                                'marking-definition--41eaaf7c-0bc0-4c56-abdf-d89a7f096ac4',
                                'marking-definition--f88d31f6-486f-44da-b317-01333bde0b82'],
                            'pattern': "[domain-name:value = 'https://somename.com']",
                            'sixgill_actor': 'abc', 'sixgill_confidence': 90,
                            'sixgill_feedid': 'darkfeed_1',
                            'sixgill_feedname': 'compromised_sites',
                            'sixgill_postid': 'cdbdb32b6323033ac9854bdd7f9133b95474de5b',
                            'sixgill_posttitle': 'https://somename.com - w/ 2 subshells',
                            'sixgill_severity': 70,
                            'sixgill_source': 'market_magbo',
                            'spec_version': '2.0', 'type': 'indicator',
                            'valid_from': '2019-12-05T18:21:55Z'}]

        self.assertEqual(indicators, expected_output)
