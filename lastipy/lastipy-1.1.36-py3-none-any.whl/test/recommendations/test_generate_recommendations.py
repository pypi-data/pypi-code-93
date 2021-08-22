import unittest
from unittest.mock import patch

from lastipy.recommendations.recommendations import generate_recommendations
from lastipy.lastfm.library.top_track import TopTrack
from lastipy.recommendations.recommended_track import RecommendedTrack


class RecommendationsGeneratorTest(unittest.TestCase):
    @patch("lastipy.recommendations.recommendations.fetch_recent_tracks")
    @patch("lastipy.recommendations.recommendations.fetch_top_tracks")
    @patch("lastipy.recommendations.recommendations.lastfm_recommendations")
    @patch("lastipy.recommendations.recommendations.calculate_ratings")
    @patch("lastipy.recommendations.recommendations.library")
    @patch("lastipy.recommendations.recommendations.playlist")
    def test_recent_tracks_are_filtered(
        self,
        mock_spotify_playlist,
        mock_spotify_library,
        mock_calculate_ratings,
        mock_fetch_recommendations,
        mock_top_tracks,
        mock_recent_tracks,
    ):
        recent_track_1 = TopTrack(track_name="SWALBR", artist="Cream", playcount=1)
        recent_track_2 = TopTrack(track_name="Badge", artist="Cream", playcount=1)
        recent_track_3 = TopTrack(
            track_name="Layla", artist="Derek & the Dominos", playcount=8
        )
        mock_recent_tracks.return_value = [
            recent_track_1,
            recent_track_2,
            recent_track_3,
        ]

        mock_top_tracks.return_value = [recent_track_3]

        new_recommendation = RecommendedTrack(
            track_name="Key to the Highway",
            artist="Derek & the Dominos",
            recommendation_rating=8,
        )
        already_scrobbled_recommendation_1 = RecommendedTrack(
            track_name="Badge", artist="Cream", recommendation_rating=8
        )
        already_scrobbled_recommendation_2 = RecommendedTrack(
            track_name="SWALBR", artist="Cream", recommendation_rating=8
        )
        recommendations = [
            new_recommendation,
            already_scrobbled_recommendation_1,
            already_scrobbled_recommendation_2,
        ]
        mock_fetch_recommendations.fetch_recommendations.return_value = recommendations

        mock_calculate_ratings.return_value = recommendations
        mock_spotify_library.get_saved_tracks.return_value = []
        mock_spotify_playlist.get_tracks_in_playlists.return_value = []

        self.assertCountEqual(
            generate_recommendations(
                spotify=None, lastfm_user="test", lastfm_api_key=""
            ),
            [new_recommendation],
        )

    @patch("lastipy.recommendations.recommendations.fetch_recent_tracks")
    @patch("lastipy.recommendations.recommendations.fetch_top_tracks")
    @patch("lastipy.recommendations.recommendations.lastfm_recommendations")
    @patch("lastipy.recommendations.recommendations.calculate_ratings")
    @patch("lastipy.recommendations.recommendations.library")
    @patch("lastipy.recommendations.recommendations.playlist")
    def test_blacklisted_artists_are_filtered(
        self,
        mock_spotify_playlist,
        mock_spotify_library,
        mock_calculate_ratings,
        mock_fetch_recommendations,
        mock_top_tracks,
        mock_recent_tracks,
    ):
        mock_recent_tracks.return_value = []
        mock_top_tracks.return_value = [
            TopTrack(track_name="Here Comes the Sun", artist="The Beatles", playcount=5)
        ]

        recommendation_1 = RecommendedTrack(
            track_name="Badge", artist="Cream", recommendation_rating=1
        )
        recommendation_2 = RecommendedTrack(
            track_name="Penny Lane", artist="The Beatles", recommendation_rating=1
        )
        recommendations = [recommendation_1, recommendation_2]
        mock_fetch_recommendations.fetch_recommendations.return_value = recommendations

        mock_calculate_ratings.return_value = recommendations
        mock_spotify_library.get_saved_tracks.return_value = []
        mock_spotify_playlist.get_tracks_in_playlists.return_value = []

        recommendations = generate_recommendations(
            lastfm_user="meeee",
            lastfm_api_key="",
            spotify=None,
            blacklisted_artists=["The Beatles"],
        )

        self.assertCountEqual(recommendations, [recommendation_1])

    @patch("lastipy.recommendations.recommendations.fetch_recent_tracks")
    @patch("lastipy.recommendations.recommendations.fetch_top_tracks")
    @patch("lastipy.recommendations.recommendations.lastfm_recommendations")
    @patch("lastipy.recommendations.recommendations.calculate_ratings")
    @patch("lastipy.recommendations.recommendations.library")
    @patch("lastipy.recommendations.recommendations.playlist")
    def test_blacklisted_artists_filtering_should_ignore_case(
        self,
        mock_spotify_playlist,
        mock_spotify_library,
        mock_calculate_ratings,
        mock_fetch_recommendations,
        mock_top_tracks,
        mock_recent_tracks,
    ):
        mock_recent_tracks.return_value = []
        mock_top_tracks.return_value = [
            TopTrack(
                track_name="everything i wanted", artist="Billie Eilish", playcount=5
            )
        ]

        recommendation = RecommendedTrack(
            track_name="Bad Music", artist="Zayn", recommendation_rating=1
        )
        recommendations = [recommendation]
        mock_fetch_recommendations.fetch_recommendations.return_value = recommendations

        mock_calculate_ratings.return_value = recommendations
        mock_spotify_library.get_saved_tracks.return_value = []
        mock_spotify_playlist.get_tracks_in_playlists.return_value = []

        recommendations = generate_recommendations(
            lastfm_user="",
            lastfm_api_key="",
            spotify=None,
            blacklisted_artists=["ZAYN"],
        )

        self.assertEqual(0, len(recommendations))
