import unittest
from lastipy.lastfm.parse_lastfm_tracks import parse_artist, parse_track_name


class ParseTracksTest(unittest.TestCase):
    def test_parse_track_name_valid_json(self):
        track_name = "Stayin' Alive"
        artist = "Bee Gees"
        to_parse = {
            "name": track_name,
            "artist": {"name": artist},
        }

        parsed_track_name = parse_track_name(to_parse)

        self.assertEqual(parsed_track_name, track_name)

    def test_parse_artist_with_weird_artist_data(self):
        track_name = "Stayin' Alive"
        artist = "Bee Gees"
        to_convert = {
            "name": track_name,
            "artist": {"mbid": "45c25199-fa62-4d4c-b0a2-11eeed6923c3", "#text": artist},
        }

        parsed_artist = parse_artist(to_convert)

        self.assertEqual(parsed_artist, artist)
