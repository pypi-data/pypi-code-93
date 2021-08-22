import logging

from lastipy.lastfm.library.top_tracks import fetch_top_tracks
from lastipy.lastfm import lastfm_recommendations
from lastipy.spotify import spotify_recommendations
from lastipy.track import Track
from lastipy.lastfm.library.recent_tracks import fetch_recent_tracks
from lastipy.recommendations.rating_calculator import calculate_ratings
from lastipy.spotify import library, search, playlist
from lastipy.lastfm.library import period
from numpy.random import choice
from lastipy.util.filter import filter_out_duplicates, filter_out_tracks_in_second_list


def generate_recommendations(
    lastfm_user,
    lastfm_api_key,
    spotify,
    recommendation_services="Last.fm",
    recommendation_period=period.OVERALL,
    max_recommendations_per_top_track=100,
    blacklisted_artists=[],
    prefer_unheard_artists=True,
):
    """Fetches recommendations for the given user based on their top tracks in Last.fm"""

    logging.info(
        "Fetching recommendations based on " + lastfm_user + "'s top tracks in Last.fm"
    )

    top_tracks = fetch_top_tracks(
        user=lastfm_user, api_key=lastfm_api_key, a_period=recommendation_period
    )

    top_tracks_to_recommendations = {}
    recommendations = []
    for top_track in top_tracks:
        try:
            recommendations_for_current_track = _fetch_recommendations(
                recommendation_services,
                lastfm_api_key,
                spotify,
                top_track,
                max_recommendations_per_top_track,
            )
            if recommendations_for_current_track:
                recommendations = recommendations + recommendations_for_current_track
                top_tracks_to_recommendations[
                    top_track
                ] = recommendations_for_current_track
        except Exception as e:
            logging.error(
                f"An error occurred fetching recommendations for track "
                + str(top_track)
                + ": "
                + str(e)
            )

    recommendations = calculate_ratings(
        user=lastfm_user,
        api_key=lastfm_api_key,
        prefer_unheard_artists=prefer_unheard_artists,
        top_tracks_to_recommendations=top_tracks_to_recommendations,
    )

    logging.debug(
        f"Before filtering, fetched "
        + str(len(recommendations))
        + " recommendations: "
        + str(recommendations)
    )
    recommendations = _filter_out_recent_tracks(
        lastfm_user, lastfm_api_key, recommendations
    )
    recommendations = _filter_out_blacklisted_artists(
        blacklisted_artists, recommendations
    )
    recommendations = _filter_out_saved_tracks(recommendations, spotify)
    recommendations = _filter_out_playlist_tracks(recommendations, spotify)
    recommendations = filter_out_duplicates(recommendations)
    logging.info(
        "After filtering, fetched " + str(len(recommendations)) + " recommendations"
    )
    logging.debug("Recommendations: " + str(recommendations))

    return recommendations


def _fetch_recommendations(
    recommendation_services, lastfm_api_key, spotify, track, limit
):
    recommendations = []
    if "Last.fm" in recommendation_services:
        recommendations += lastfm_recommendations.fetch_recommendations(
            api_key=lastfm_api_key, limit=limit, track=track
        )
    if "Spotify" in recommendation_services:
        recommendations += spotify_recommendations.fetch_recommendations(
            spotify=spotify, track=track, limit=limit
        )
    return recommendations


def _filter_out_recent_tracks(user, api_key, recommendations):
    logging.info("Filtering out recent tracks from recommendations")
    recent_tracks = fetch_recent_tracks(user, api_key)
    return filter_out_tracks_in_second_list(recommendations, recent_tracks)


def _filter_out_blacklisted_artists(blacklisted_artists, recommendations):
    logging.info(
        "Filtering out blacklisted artists ("
        + str(blacklisted_artists)
        + ") from recommendations"
    )
    recommendations = [
        recommendation
        for recommendation in recommendations
        if not any(
            recommendation.artist.lower() == blacklisted_artist.lower()
            for blacklisted_artist in blacklisted_artists
        )
    ]
    return recommendations


# TODO test
def _filter_out_saved_tracks(recommendations, spotify):
    logging.info("Filtering out saved tracks from recommendations")
    saved_tracks = library.get_saved_tracks(spotify)
    return filter_out_tracks_in_second_list(recommendations, saved_tracks)


# TODO test
def _filter_out_playlist_tracks(recommendations, spotify):
    logging.info("Filtering out tracks in the user's playlists from recommendations")
    playlist_tracks = playlist.get_tracks_in_playlists(spotify)
    return filter_out_tracks_in_second_list(recommendations, playlist_tracks)
