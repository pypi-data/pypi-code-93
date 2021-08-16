from unittest import TestCase
from mock import patch
import logging
import requests
import json

from sixgill.sixgill_base_client import SixgillBaseClient
from sixgill.sixgill_exceptions import AuthException


class MockedResponse(object):
    def __init__(self, status_code, text, reason=None, url=None, method=None):
        self.status_code = status_code
        self.text = text
        self.reason = reason
        self.url = url
        self.request = requests.Request('GET')

    def json(self):
        return json.loads(self.text)


class TestSixgillBaseClient(TestCase):

    def setUp(self):
        self.sixgill_client = SixgillBaseClient('client_id', 'secret', 'random', logging.getLogger("test"))
        self.mocked_incidents_response = mocked_incidents_response
        self.mocked_get_token_response = mocked_get_token_response
        self.mocked_alerts_response = mocked_alerts_response
        self.mocked_put_response = mocked_put_response
        self.mock_enrich_response = mock_enrich_response

        self.bundle = 0
        self.submitted_indicators = 0

    def mocked_request(self, *args, **kwargs):
        request = kwargs.get("request", {})
        end_point = request.path_url
        method = request.method

        if (method == 'PUT') and request.body:
            self.mocked_incidents_response = '''[]'''
            self.mocked_alerts_response = '''[]'''

        self.response_dict = {
            'POST': {
                '/auth/token':
                    MockedResponse(200, self.mocked_get_token_response),
                '/darkfeed/ioc/ack':
                    MockedResponse(200, str(self.submitted_indicators)),
                '/darkfeed_freemium/ioc/ack':
                    MockedResponse(200, str(self.submitted_indicators)),
                '/ioc/enrich':
                    MockedResponse(200, json.dumps(self.mock_enrich_response))
            },
            'GET': {
                '/alerts/feed/alerts?include_delivered_items=False&limit=1000&skip=0':
                    MockedResponse(200, json.dumps(json.loads(self.mocked_alerts_response))),
                '/alerts/feed/alerts?include_delivered_items=False&skip=0&limit=1000':
                    MockedResponse(200, json.dumps(json.loads(self.mocked_alerts_response))),
                '/darkfeed/ioc?limit=7':
                    MockedResponse(200, json.dumps(self.mocked_incidents_response[self.bundle])),
                '/darkfeed_freemium/ioc?limit=7':
                    MockedResponse(200, json.dumps(self.mocked_incidents_response[self.bundle]))
            },
            'PUT': {
                '/alerts/feed?consumer=random': MockedResponse(200, self.mocked_put_response)
            },
        }

        response_dict = self.response_dict.get(method)
        response = response_dict.get(end_point)

        if ((method == 'GET' and end_point == '/darkfeed/ioc?limit=7') or
                (method == 'GET' and end_point == '/darkfeed_freemium/ioc?limit=7')):
            self.submitted_indicators = len(mocked_incidents_response[self.bundle].get("objects")) - 2
            self.bundle += 1

        return response

    def mocked_bad_request(self, *args, **kwargs):
        return MockedResponse(404, self.mocked_get_token_response, "Bad request", '/mocked_url')

    def test_get_access_token(self):
        with patch('requests.sessions.Session.send', new=self.mocked_request):
            access_token = self.sixgill_client._get_access_token()

        expected_output = "this_is_my_token"
        self.assertEqual(access_token, expected_output)

    def test_bad_access_token(self):
        with patch('requests.sessions.Session.send', new=self.mocked_bad_request):
            self.assertRaises(AuthException, self.sixgill_client._get_access_token)


mocked_get_token_response = '''{"access_token": "this_is_my_token"}'''
mocked_put_response = '''{"status": 200, "message": "Successfully Marked as Ingested Feed Items"}'''

mocked_alerts_response = '''[
    {
        "alert_name": "someSecretAlert2",
        "content": "",
        "date": "2019-08-06 23:20:35", 
        "id": "1", 
        "lang": "English", 
        "langcode": "en",
        "read": false, 
        "severity": 10, 
        "threat_level": "emerging", 
        "threats": ["Phishing"],
        "title": "someSecretAlert2", 
        "user_id": "123"},
    {
        "alert_name": "someSecretAlert4",
        "content": "",
        "date": "2019-08-18 09:58:10", 
        "id": "2", 
        "read": false, 
        "severity": 10,
        "threat_level": "imminent", 
        "threats": ["Data Leak", "Phishing"], 
        "title": "someSecretAlert4",
        "user_id": "132"}, 
    {
        "alert_name": "someSecretAlert1",
         "content": "",
         "date": "2019-08-18 22:58:23",
         "id": "3", 
         "read": false,
         "severity": 10, 
         "threat_level": "imminent",
         "threats": ["Data Leak", "Phishing"],
         "title": "someSecretAlert1",
         "user_id": "123"},
    {
        "alert_name": "someSecretAlert2",
        "content": "",
        "date": "2019-08-19 19:27:24", 
        "id": "4", 
        "lang": "English", 
        "langcode": "en",
        "read": false, 
        "severity": 10, 
        "threat_level": "emerging", 
        "threats": ["Phishing"],
        "title": "someSecretAlert2", 
        "user_id": "123"},
    {
        "alert_name": "someSecretAlert3",
        "content": "",
        "date": "2019-08-22 08:27:19",
        "id": "5", 
        "read": false, 
        "severity": 10,
        "threat_level": "imminent", 
        "threats": ["Data Leak", "Phishing"], 
        "title": "someSecretAlert3",
        "user_id": "123"}, 
    {
        "alert_name": "someSecretAlert1",
        "content": "",
        "date": "2019-08-22 08:43:15",
        "id": "6", 
        "read": false,
        "severity": 10, 
        "threat_level": "imminent",
        "threats": ["Data Leak", "Phishing"],
        "title": "someSecretAlert1",
        "user_id": "123"
    }]'''

mocked_incidents_response = [{'id': 'bundle--bcbb94ea-2d3a-43f1-8c1a-62002594d2ba',
                             'objects': [{'created': '2017-01-20T00:00:00.000Z', 'definition': {'tlp': 'amber'},
                                          'definition_type': 'tlp',
                                          'id': 'marking-definition--f88d31f6-486f-44da-b317-01333bde0b82',
                                          'type': 'marking-definition'},
                                         {'created': '2019-12-26T00:00:00Z',
                                          'definition': {'statement': 'Copyright Sixgill 2020. All rights reserved.'},
                                          'definition_type': 'statement',
                                          'id': 'marking-definition--41eaaf7c-0bc0-4c56-abdf-d89a7f096ac4',
                                          'type': 'marking-definition'},
                                         {'created': '2020-01-09T07:31:10.991Z',
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
                                          'id': 'indicator--851269aa-f9f9-4375-a5af-3fbe35729fb7',
                                          'kill_chain_phases': [
                                              {'kill_chain_name': 'some-name',
                                               'phase_name': 'abc'}],
                                          'labels': ['compromised', 'shell', 'webshell'], 'lang': 'ru',
                                          'modified': '2020-01-09T07:31:11.007Z',
                                          'object_marking_refs': [
                                              'marking-definition--41eaaf7c-0bc0-4c56-abdf-d89a7f096ac4',
                                              'marking-definition--f88d31f6-486f-44da-b317-01333bde0b82'],
                                          'pattern': "[domain-name:value = 'https://someweb.no']",
                                          'sixgill_actor': 'abc',
                                          'sixgill_confidence': 90, 'sixgill_feedid': 'darkfeed_1',
                                          'sixgill_feedname': 'compromised_sites',
                                          'sixgill_postid': '5cd7f37cffa1687f271750196fe616f1179d2d04',
                                          'sixgill_posttitle': 'https://someweb.no',
                                          'sixgill_severity': 70, 'sixgill_source': 'market_magbo',
                                          'spec_version': '2.0',
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
                                          'id': 'indicator--7aaa8d80-ff19-47bc-ad8c-f6a94c4f88fd',
                                          'kill_chain_phases': [
                                              {'kill_chain_name': 'some-name',
                                               'phase_name': 'abc'}],
                                          'labels': ['compromised', 'shell', 'webshell'], 'lang': 'en',
                                          'modified': '2020-01-09T07:31:11.037Z',
                                          'object_marking_refs': [
                                              'marking-definition--41eaaf7c-0bc0-4c56-abdf-d89a7f096ac4',
                                              'marking-definition--f88d31f6-486f-44da-b317-01333bde0b82'],
                                          'pattern': "[domain-name:value = 'http://somewebsite.com']",
                                          'sixgill_actor': 'abc',
                                          'sixgill_confidence': 90, 'sixgill_feedid': 'darkfeed_1',
                                          'sixgill_feedname': 'compromised_sites',
                                          'sixgill_postid': '86dbf0af5ba1aef05e2b60267043c55327a897dd',
                                          'sixgill_posttitle': 'http://somewebsite.com',
                                          'sixgill_severity': 70, 'sixgill_source': 'market_magbo',
                                          'spec_version': '2.0',
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
                                          'valid_from': '2019-12-05T18:21:55Z'}
                                         ],
                             'spec_version': '2.0', 'type': 'bundle'},
                            {'id': 'bundle--bcbb94ea-2d3a-43f1-8c1a-62002594d2bb',
                             'objects': [{'created': '2017-01-20T00:00:00.000Z', 'definition': {'tlp': 'amber'},
                                          'definition_type': 'tlp',
                                          'id': 'marking-definition--f88d31f6-486f-44da-b317-01333bde0b82',
                                          'type': 'marking-definition'},
                                         {'created': '2019-12-26T00:00:00Z',
                                          'definition': {'statement': 'Copyright Sixgill 2020. All rights reserved.'},
                                          'definition_type': 'statement',
                                          'id': 'marking-definition--41eaaf7c-0bc0-4c56-abdf-d89a7f096ac4',
                                          'type': 'marking-definition'}],
                             'spec_version': '2.0', 'type': 'bundle'}
                             ]

mock_enrich_response = {"items": [
                            {
                                "created": "2012-04-27T05:00:12.160Z",
                                "description": "Some Description",
                                "external_reference": [
                                    {
                                        "description": "Mitre attack tactics and technique reference",
                                        "mitre_attack_tactic": "Mitre Tactic",
                                        "mitre_attack_tactic_id": "TA1234",
                                        "mitre_attack_tactic_url": "https://attack.mitre.org/tactics/TA1234/",
                                        "source_name": "mitre-attack"
                                    }
                                ],
                                "id": "indicator--some-indicator",
                                "labels": [
                                    "label1",
                                    "label2"
                                ],
                                "lang": "En",
                                "modified": "2012-04-27T05:00:12.160Z",
                                "pattern": "[ipv4-addr:value = 'some ip address']",
                                "sixgill_actor": "Iron Man",
                                "sixgill_confidence": 90,
                                "sixgill_feedid": "Mark XLIV",
                                "sixgill_feedname": "Hulkbuster",
                                "sixgill_postid": "1234",
                                "sixgill_posttitle": "Age Of Ultron",
                                "sixgill_severity": 90,
                                "sixgill_source": "Marvel",
                                "spec_version": "2.0",
                                "type": "indicator",
                                "valid_from": "2012-04-27T04:59:07Z"
                            }
                              ],
                              "total": 2
                            }
