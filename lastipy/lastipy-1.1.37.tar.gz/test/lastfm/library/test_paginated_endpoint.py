import unittest
from unittest.mock import patch
from unittest.mock import Mock
from requests import HTTPError
from lastipy.track import Track
from lastipy.lastfm.library.paginated_endpoint import fetch_paginated_response


class RecentArtistsTest(unittest.TestCase):

    dummy_url = "www.example.org"
    dummy_user = "dummyUser"
    dummy_api_key = "123456789"

    @patch("requests.get")
    def test_fetch_single_page(self, mock_requests_get):
        mock_response = Mock()
        mock_response.ok = True
        json_object_page = {
            "arrayKey": {
                "array": [
                    {"key1": "Value1", "key2": {"key3": "Value2"}},
                    {"key1": "Value3", "key2": {"key3": "Value4"}},
                ],
                "@attr": {"totalPages": "1"},
            }
        }
        mock_response.json.return_value = json_object_page
        mock_requests_get.side_effect = [mock_response]

        fetched_objects = fetch_paginated_response(
            self.dummy_url, self.dummy_user, self.dummy_api_key, "arrayKey"
        )

        self.assertCountEqual(fetched_objects, [json_object_page])

    @patch("requests.get")
    def test_fetch_multiple_pages(self, mock_requests_get):
        json_object_page_1 = {
            "arrayKey": {
                "array": [
                    {"key1": "Value1", "key2": "Value2"},
                    {"key1": "Value3", "key2": "Value4"},
                ],
                "@attr": {"totalPages": "3"},
            }
        }
        json_object_page_2 = {
            "arrayKey": {
                "array": [
                    {"key1": "Value5", "key2": "Value6"},
                    {"key1": "Value7", "key2": "Value8"},
                ],
                "@attr": {"totalPages": "3"},
            }
        }
        json_object_page_3 = {
            "arrayKey": {
                "array": [
                    {"key1": "Value9", "key2": "Value10"},
                    {"key1": "Value11", "key2": "Value12"},
                ],
                "@attr": {"totalPages": "3"},
            }
        }

        mock_responses = [Mock(), Mock(), Mock()]
        mock_responses[0].ok = True
        mock_responses[0].json.return_value = json_object_page_1
        mock_responses[1].ok = True
        mock_responses[1].json.return_value = json_object_page_2
        mock_responses[2].ok = True
        mock_responses[2].json.return_value = json_object_page_3
        mock_requests_get.side_effect = mock_responses

        fetched_objects = fetch_paginated_response(
            self.dummy_url, self.dummy_user, self.dummy_api_key, "arrayKey"
        )

        self.assertCountEqual(
            fetched_objects,
            [json_object_page_1, json_object_page_2, json_object_page_3],
        )

    @patch("requests.get")
    def test_fetch_with_success_after_retries(self, mock_requests_get):
        json_object_page_1 = {
            "arrayKey": {
                "array": [
                    {"key1": "Value1", "key2": "Value2"},
                    {"key1": "Value3", "key2": "Value4"},
                ],
                "@attr": {"totalPages": "2"},
            }
        }

        json_object_page_2 = {
            "arrayKey": {
                "array": [
                    {"key1": "Value5", "key2": "Value6"},
                    {"key1": "Value7", "key2": "Value8"},
                ],
                "@attr": {"totalPages": "2"},
            }
        }

        mock_responses = [Mock(), Mock(), Mock()]
        mock_responses[0].ok = True
        mock_responses[0].json.return_value = json_object_page_1
        mock_responses[1].ok = False
        mock_responses[1].raise_for_status.side_effect = HTTPError(
            Mock(status=500), "Error"
        )
        mock_responses[2].ok = True
        mock_responses[2].json.return_value = json_object_page_2
        mock_requests_get.side_effect = mock_responses

        fetched_objects = fetch_paginated_response(
            self.dummy_url, self.dummy_user, self.dummy_api_key, "arrayKey"
        )

        self.assertCountEqual(fetched_objects, [json_object_page_1, json_object_page_2])

    @patch("requests.get")
    def test_fetch_fails_after_retries(self, mock_requests_get):
        mock_responses = []
        for _ in range(11):
            mock_response = Mock()
            mock_response.ok = False
            mock_response.raise_for_status.side_effect = HTTPError(
                Mock(status=500), "Error"
            )
            mock_responses.append(mock_response)

        # Add another mock response, but the code will exit after the retry limit is reached and this won't actually get fetched
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"test"}
        mock_responses.append(mock_response)

        mock_requests_get.side_effect = mock_responses

        fetched_objects = fetch_paginated_response(
            self.dummy_url, self.dummy_user, self.dummy_api_key, "arrayKey"
        )

        self.assertCountEqual(fetched_objects, [])

    @patch("requests.get")
    def test_extra_request_params(self, mock_requests_get):
        mock_requests_get.ok = True
        mock_requests_get.json.return_value = []

        fetch_paginated_response(
            self.dummy_url,
            self.dummy_user,
            self.dummy_api_key,
            "arrayKey",
            [{"key": "key1", "value": "value1"}, {"key": "key2", "value": "value2"}],
        )

        expected_request = {
            "user": self.dummy_user,
            "format": "json",
            "api_key": self.dummy_api_key,
            "limit": 200,
            "page": 1,
            "key1": "value1",
            "key2": "value2",
        }

        mock_requests_get.assert_called_with(self.dummy_url, params=expected_request)
