from mock import patch
import logging
import json

from sixgill.sixgill_alert_client import SixgillAlertClient
from tests.test_sixgill_base_client import TestSixgillBaseClient


class TestSixgillAlertClient(TestSixgillBaseClient):

    def setUp(self):
        super(TestSixgillAlertClient, self).setUp()
        self.sixgill_alert_client = SixgillAlertClient('client_id', 'secret', 'random', logging.getLogger("test"))

    def test_get_alerts(self):
        with patch('requests.sessions.Session.send', new=self.mocked_request):
            alerts = []
            for alert in self.sixgill_alert_client.get_alert():
                self.sixgill_alert_client.mark_digested_item(alert)
                alerts.append(alert)

        expected_output = [{'alert_name': 'someSecretAlert2', 'content': '', 'date': '2019-08-06 23:20:35', 'id': '1',
                            'lang': 'English', 'langcode': 'en', 'read': False, 'severity': 10,
                            'threat_level': 'emerging', 'threats': ['Phishing'], 'title': 'someSecretAlert2',
                            'user_id': '123'},
                           {'alert_name': 'someSecretAlert4', 'content': '', 'date': '2019-08-18 09:58:10', 'id': '2',
                            'read': False, 'severity': 10, 'threat_level': 'imminent',
                            'threats': ['Data Leak', 'Phishing'], 'title': 'someSecretAlert4', 'user_id': '132'},
                           {'alert_name': 'someSecretAlert1', 'content': '', 'date': '2019-08-18 22:58:23', 'id': '3',
                            'read': False, 'severity': 10, 'threat_level': 'imminent',
                            'threats': ['Data Leak', 'Phishing'], 'title': 'someSecretAlert1', 'user_id': '123'},
                           {'alert_name': 'someSecretAlert2', 'content': '', 'date': '2019-08-19 19:27:24', 'id': '4',
                            'lang': 'English', 'langcode': 'en', 'read': False, 'severity': 10,
                            'threat_level': 'emerging', 'threats': ['Phishing'], 'title': 'someSecretAlert2',
                            'user_id': '123'},
                           {'alert_name': 'someSecretAlert3', 'content': '', 'date': '2019-08-22 08:27:19', 'id': '5',
                            'read': False, 'severity': 10, 'threat_level': 'imminent',
                            'threats': ['Data Leak', 'Phishing'], 'title': 'someSecretAlert3', 'user_id': '123'},
                           {'alert_name': 'someSecretAlert1', 'content': '', 'date': '2019-08-22 08:43:15', 'id': '6',
                            'read': False, 'severity': 10, 'threat_level': 'imminent',
                            'threats': ['Data Leak', 'Phishing'], 'title': 'someSecretAlert1', 'user_id': '123'}]

        self.assertEqual(alerts, expected_output)

    def test_mark_and_commit(self):
        with patch('requests.sessions.Session.send', new=self.mocked_request):
            alerts = json.loads(self.mocked_alerts_response)

            for alert in alerts:
                self.sixgill_alert_client.mark_digested_item(alert)

            expected_output = ["1", "2", "3", "4", "5", "6"]
            self.assertEqual(self.sixgill_alert_client.digested_ids, expected_output)

            self.sixgill_alert_client.commit_digested_items(force=True)

            self.assertEqual(self.sixgill_alert_client.digested_ids, [])
