import unittest
from lastipy.lastfm.library.top_track import TopTrack
from lastipy.recommendations.recommended_track import RecommendedTrack
from unittest.mock import patch
from lastipy.lastfm.lastfm_recommendations import fetch_recommendations


class LastFmRecommendationsTest(unittest.TestCase):
    @patch("requests.get")
    def test_track_has_multiple_similar_tracks(self, mock_requests_get):
        playcount = 5
        track_to_check = TopTrack(
            track_name="Night Fever", artist="Bee Gees", playcount=playcount
        )
        expected_similar_tracks = [
            RecommendedTrack(
                track_name="Stayin' Alive", artist="Bee Gees", recommendation_rating=1
            ),
            RecommendedTrack(
                track_name="You Should Be Dancing",
                artist="Bee Gees",
                recommendation_rating=1,
            ),
        ]

        json_tracks = []
        for track in expected_similar_tracks:
            json_track = {
                "name": track.track_name,
                "artist": {"name": track.artist},
                "match": track.recommendation_rating,
            }
            json_tracks.append(json_track)

        json_response = {"similartracks": {"track": json_tracks}}

        mock_requests_get.return_value.json.return_value = json_response

        fetched_tracks = fetch_recommendations("", track_to_check, 2)
        self.assertCountEqual(expected_similar_tracks, fetched_tracks)
