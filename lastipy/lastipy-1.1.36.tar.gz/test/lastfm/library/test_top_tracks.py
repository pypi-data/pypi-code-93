import unittest
from lastipy.lastfm.library import period
from lastipy.lastfm.library.top_track import TopTrack
from unittest.mock import patch, Mock
from requests import HTTPError
from lastipy.lastfm.library.top_tracks import fetch_top_tracks


class TopTracksFetcherTest(unittest.TestCase):

    dummy_user = "dummyUser"
    dummy_api_key = "123456789"

    @patch("lastipy.lastfm.library.top_tracks.fetch_paginated_response")
    def test_one_page_of_results(self, mock_paginated_endpoint_fetch):
        expected_track_1 = TopTrack(
            track_name="Stayin Alive", artist="Bee Gees", playcount=2
        )
        expected_track_2 = TopTrack(track_name="Badge", artist="Cream", playcount=7)

        json_response_page_1 = {
            "toptracks": {
                "track": [
                    {
                        "name": "Stayin Alive",
                        "artist": {"name": "Bee Gees"},
                        "playcount": "2",
                    }
                ]
            }
        }

        json_response_page_2 = {
            "toptracks": {
                "track": [
                    {"name": "Badge", "artist": {"name": "Cream"}, "playcount": "7"}
                ]
            }
        }

        mock_paginated_endpoint_fetch.return_value = [
            json_response_page_1,
            json_response_page_2,
        ]

        fetched_tracks = fetch_top_tracks(
            user=self.dummy_user, api_key=self.dummy_api_key, a_period=period.ONE_MONTH
        )
        self.assertCountEqual(fetched_tracks, [expected_track_1, expected_track_2])

    @patch("lastipy.lastfm.library.top_tracks.fetch_paginated_response")
    def test_songs_with_one_playcount_ignored(self, mock_paginated_endpoint_fetch):
        json_response_page = {
            "toptracks": {
                "track": [
                    {
                        "name": "Stayin Alive",
                        "artist": {"name": "Bee Gees"},
                        "playcount": "1",
                    }
                ]
            }
        }

        mock_paginated_endpoint_fetch.return_value = [json_response_page]

        fetched_tracks = fetch_top_tracks(
            user=self.dummy_user, api_key=self.dummy_api_key, a_period=period.ONE_MONTH
        )
        self.assertCountEqual(fetched_tracks, [])
