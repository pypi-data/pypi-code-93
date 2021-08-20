import unittest
from unittest.mock import patch
from lastipy.lastfm.library import recent_tracks
from unittest.mock import Mock
from requests import HTTPError
from lastipy.track import Track


class RecentArtistsTest(unittest.TestCase):

    dummy_user = "dummyUser"
    dummy_api_key = "123456789"

    @patch("lastipy.lastfm.library.recent_tracks.fetch_paginated_response")
    def test_fetch(self, mock_paginated_endpoint_fetch):
        expected_tracks = [
            Track(track_name="Strawberry Fields Forever", artist="The Beatles"),
            Track(track_name="Badge", artist="Cream"),
            Track(track_name="Black Dog", artist="Led Zeppelin"),
        ]

        mock_paginated_endpoint_fetch.return_value = [
            {
                "recenttracks": {
                    "track": [
                        {
                            "name": "Strawberry Fields Forever",
                            "artist": {"name": "The Beatles"},
                        },
                        {"name": "Badge", "artist": {"name": "Cream"}},
                    ],
                    "@attr": {"totalPages": "2"},
                }
            },
            {
                "recenttracks": {
                    "track": [
                        {"name": "Black Dog", "artist": {"name": "Led Zeppelin"}}
                    ],
                    "@attr": {"totalPages": "2"},
                }
            },
        ]

        fetched_tracks = recent_tracks.fetch_recent_tracks(
            user=self.dummy_user, api_key=self.dummy_api_key
        )

        self.assertCountEqual(fetched_tracks, expected_tracks)
