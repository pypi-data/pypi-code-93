# pylint: disable=missing-docstring,no-self-use,line-too-long

import unittest
from unittest.mock import patch,  MagicMock
from typing import NamedTuple, Optional, Dict
from json import dumps
import soil


class MockHttpResponse(NamedTuple):
    ''' Soil configuration class '''
    status_code: int
    text: str


# pylint: disable=unused-argument
def mock_http_post(url: str,
                   headers: Optional[Dict[str, str]] = None,
                   json: Optional[Dict[str, str]] = None
                   ) -> MockHttpResponse:
    assert json is not None
    response = 'ok'
    return MockHttpResponse(status_code=201, text=dumps(response))


class TestAlerts(unittest.TestCase):

    @patch('soil.api.requests.post', side_effect=mock_http_post)
    def test_create_event(self, mock_post: MagicMock) -> None:
        soil.alerts.event('test_key', 'test_value')
        mock_post.assert_called_once_with(
            'http://test_host.test/v2/alerts/events/',
            headers={'Authorization': 'Bearer test_token'},
            json={'key': 'test_key', 'value': 'test_value'})

    @patch('soil.api.requests.post', side_effect=mock_http_post)
    def test_create_alert(self, mock_post: MagicMock) -> None:
        alert_config = {
            "role": "test_alerts",
            "event_id": "test_event1",
            "condition": {
                "type": "any"
            }
        }
        soil.alerts.alert(alert_config)
        mock_post.assert_called_once_with(
            'http://test_host.test/v2/alerts/alerts/',
            headers={'Authorization': 'Bearer test_token'},
            json=alert_config)
