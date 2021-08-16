from mock import patch

from tests.test_sixgill_base_client import TestSixgillBaseClient
from sixgill.sixgill_enrich_client import SixgillEnrichClient

class TestSixgillEnrichClient(TestSixgillBaseClient):

    def setUp(self):
        super(TestSixgillEnrichClient, self).setUp()
        self.sixgill_enrich_client = SixgillEnrichClient('client_id', 'secret', 'random')

    def test_enrich_postid(self):
        with patch('requests.sessions.Session.send', new=self.mocked_request):
            enrich_data = self.sixgill_enrich_client.enrich_postid("1234567890asdfghjkl", 0)
        expected_output = [
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
                            },
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
                          ]
        self.assertEqual(enrich_data, expected_output)

    def test_enrich_actor(self):
        with patch('requests.sessions.Session.send', new=self.mocked_request):
            enrich_data = self.sixgill_enrich_client.enrich_actor("IronMan")
        expected_output = [
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
                            },
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
                          ]
        self.assertEqual(enrich_data, expected_output)

    def test_enrich_actor(self):
        with patch('requests.sessions.Session.send', new=self.mocked_request):
            enrich_data = self.sixgill_enrich_client.enrich_ioc("ip", "1.1.1.1")
        expected_output = [
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
                            },
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
                          ]
        self.assertEqual(enrich_data, expected_output)
