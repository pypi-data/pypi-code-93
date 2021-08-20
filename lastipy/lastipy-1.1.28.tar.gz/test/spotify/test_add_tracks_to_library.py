import unittest
from lastipy.spotify.library import add_tracks_to_library
from spotipy import Spotify
from lastipy.track import Track


class AddTracksToLibraryTest(unittest.TestCase):
    def test_adding_less_than_max_request(self):
        spotify = Spotify()
        spotify.current_user = unittest.mock.MagicMock({"id": "testUser"})
        spotify.current_user_saved_tracks_add = unittest.mock.MagicMock()
        dummy_tracks = [
            self._build_dummy_track("123"),
            self._build_dummy_track("456"),
            self._build_dummy_track("789"),
        ]
        add_tracks_to_library(spotify, dummy_tracks)
        spotify.current_user_saved_tracks_add.assert_called_with(["123", "456", "789"])

    def test_adding_more_than_max_request(self):
        spotify = Spotify()
        spotify.current_user = unittest.mock.MagicMock({"id": "testUser"})
        spotify.current_user_saved_tracks_add = unittest.mock.MagicMock()

        dummy_tracks = []
        for _ in range(150):
            dummy_tracks.append(self._build_dummy_track("123"))

        expected_chunks = []
        for _ in range(3):
            chunk = []
            for _ in range(50):
                chunk.append("123")
            expected_chunks.append(chunk)

        add_tracks_to_library(spotify, dummy_tracks)

        for i in range(3):
            spotify.current_user_saved_tracks_add.assert_called_with(expected_chunks[i])

    def _build_dummy_track(self, spotify_id):
        return Track(
            spotify_id=spotify_id, track_name="dummy_track_name", artist="dummy_artist"
        )
