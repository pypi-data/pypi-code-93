import unittest
from unittest.mock import patch
from lastipy.lastfm.library import recent_artists
from unittest.mock import Mock
from requests import HTTPError
from lastipy.lastfm.library.scrobbled_artist import ScrobbledArtist


class RecentArtistsTest(unittest.TestCase):

    dummy_user = "dummyUser"
    dummy_api_key = "123456789"

    @patch("lastipy.lastfm.library.recent_artists.fetch_paginated_response")
    def test_fetch(self, mock_paginated_endpoint_fetch):
        expected_artists = [
            ScrobbledArtist(artist_name="The Beatles", playcount=10),
            ScrobbledArtist(artist_name="Cream", playcount=4),
            ScrobbledArtist(artist_name="Led Zeppelin", playcount=7),
        ]

        mock_paginated_endpoint_fetch.return_value = [
            {
                "artists": {
                    "artist": [
                        {"name": "The Beatles", "playcount": "10"},
                        {"name": "Cream", "playcount": "4"},
                    ],
                    "@attr": {"totalPages": "2"},
                }
            },
            {
                "artists": {
                    "artist": [{"name": "Led Zeppelin", "playcount": "7"}],
                    "@attr": {"totalPages": "2"},
                }
            },
        ]

        fetched_artists = recent_artists.fetch_recent_artists(
            user=self.dummy_user, api_key=self.dummy_api_key
        )

        self.assertCountEqual(fetched_artists, expected_artists)
