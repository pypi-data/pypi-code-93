import unittest
from unittest.mock import MagicMock
from spotipy import Spotify
from lastipy.spotify.library import get_saved_tracks
from lastipy.track import Track


class GetSavedTracksTest(unittest.TestCase):
    def setUp(self):
        self.mock_spotify = Spotify()
        self.mock_spotify.current_user = MagicMock({"id": "dummyUser"})

    def test_fetch_single_page(self):
        expected_saved_tracks = [
            Track(track_name="Penny Lane", artist="The Beatles", spotify_id="123456789")
        ]

        self.mock_spotify.current_user_saved_tracks = MagicMock()
        mock_saved_tracks_response = {
            "items": [
                {
                    "id": "123456789",
                    "name": "Penny Lane",
                    "artists": [{"name": "The Beatles"}],
                }
            ]
        }
        self.mock_spotify.current_user_saved_tracks.side_effect = [
            mock_saved_tracks_response,
            {"items": []},
        ]

        fetched_saved_tracks = get_saved_tracks(self.mock_spotify)

        self.assertCountEqual(fetched_saved_tracks, expected_saved_tracks)

    def test_fetch_multiple_pages(self):
        expected_saved_tracks = [
            Track(
                track_name="Penny Lane", artist="The Beatles", spotify_id="123456789"
            ),
            Track(
                track_name="A Day in the Life",
                artist="The Beatles",
                spotify_id="987654321",
            ),
        ]

        self.mock_spotify.current_user_saved_tracks = MagicMock()
        mock_saved_tracks_response_page_1 = {
            "items": [
                {
                    "id": "123456789",
                    "name": "Penny Lane",
                    "artists": [{"name": "The Beatles"}],
                }
            ]
        }
        mock_saved_tracks_response_page_2 = {
            "items": [
                {
                    "id": "987654321",
                    "name": "A Day in the Life",
                    "artists": [{"name": "The Beatles"}],
                }
            ]
        }
        self.mock_spotify.current_user_saved_tracks.side_effect = [
            mock_saved_tracks_response_page_1,
            mock_saved_tracks_response_page_2,
            {"items": []},
        ]

        fetched_saved_tracks = get_saved_tracks(self.mock_spotify)

        self.assertCountEqual(fetched_saved_tracks, expected_saved_tracks)
