import unittest
from unittest.mock import patch
from lastipy.lastfm.library.track_info import fetch_playcount
from lastipy.track import Track
from unittest.mock import Mock
from requests import HTTPError


class FetchPlaycountTest(unittest.TestCase):

    dummy_track = Track(track_name="Dummy Track", artist="Dummy Artist")

    @patch("requests.get")
    def test_successful_fetch(self, mock_requests_get):
        json_response = {"track": {"userplaycount": "5"}}

        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = json_response
        mock_requests_get.side_effect = [mock_response]

        fetched_playcount = fetch_playcount(
            track=self.dummy_track, user="dummyUser", api_key="dummyApiKey"
        )

        self.assertEqual(fetched_playcount, 5)

    @patch("requests.get")
    def test_successful_fetch_after_retries(self, mock_requests_get):
        json_response = {"track": {"userplaycount": "7"}}

        mock_responses = [Mock(), Mock(), Mock()]
        mock_responses[0].ok = False
        mock_responses[0].raise_for_status.side_effect = HTTPError(
            Mock(status=500), "Error"
        )
        mock_responses[1] = mock_responses[0]
        mock_responses[2].ok = True
        mock_responses[2].json.return_value = json_response
        mock_requests_get.side_effect = mock_responses

        fetched_playcount = fetch_playcount(
            track=self.dummy_track, user="dummyUser", api_key="dummyApiKey"
        )

        self.assertEqual(fetched_playcount, 7)

    @patch("requests.get")
    def test_failure_after_retries(self, mock_requests_get):
        mock_responses = []
        for _ in range(11):
            mock_response = Mock()
            mock_response.ok = False
            mock_response.raise_for_status.side_effect = HTTPError(
                Mock(status=500), "Error"
            )
            mock_responses.append(mock_response)

        mock_requests_get.side_effect = mock_responses

        fetched_playcount = fetch_playcount(
            track=self.dummy_track, user="dummyUser", api_key="dummyApiKey"
        )

        self.assertEqual(0, fetched_playcount)
