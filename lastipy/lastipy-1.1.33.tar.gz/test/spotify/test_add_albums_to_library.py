import unittest
from lastipy.spotify.library import add_albums_to_library
from spotipy import Spotify
from lastipy.spotify.album import SpotifyAlbum


class AddAlbumsToLibraryTest(unittest.TestCase):
    def test_adding_less_than_max_request(self):
        spotify = Spotify()
        spotify.current_user = unittest.mock.MagicMock({"id": "testUser"})
        spotify.current_user_saved_albums_add = unittest.mock.MagicMock()
        dummy_albums = [
            self._build_dummy_album("123"),
            self._build_dummy_album("456"),
            self._build_dummy_album("789"),
        ]
        add_albums_to_library(spotify, dummy_albums)
        spotify.current_user_saved_albums_add.assert_called_with(["123", "456", "789"])

    def test_adding_more_than_max_request(self):
        spotify = Spotify()
        spotify.current_user = unittest.mock.MagicMock({"id": "testUser"})
        spotify.current_user_saved_albums_add = unittest.mock.MagicMock()

        dummy_albums = []
        for _ in range(150):
            dummy_albums.append(self._build_dummy_album("123"))

        expected_chunks = []
        for _ in range(3):
            chunk = []
            for _ in range(50):
                chunk.append("123")
            expected_chunks.append(chunk)

        add_albums_to_library(spotify, dummy_albums)

        for i in range(3):
            spotify.current_user_saved_albums_add.assert_called_with(expected_chunks[i])

    def _build_dummy_album(self, spotify_id):
        return SpotifyAlbum(
            name="test_name",
            artist="test_artist",
            spotify_id=spotify_id,
            album_type="album",
            release_date_precision="day",
            release_date="2000-01-01",
        )
