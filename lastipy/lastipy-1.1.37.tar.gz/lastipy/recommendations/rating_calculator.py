import copy
import logging
from lastipy.lastfm.library.recent_artists import fetch_recent_artists


def calculate_ratings(
    user, api_key, top_tracks_to_recommendations, prefer_unheard_artists=True
):
    """Returns a copy of the list of recommendations in the given map, with ratings set based on recommendation
    'strength', which can be used to determine its chances of showing up in the final playlist"""

    logging.info("Adjusting track recommendation ratings")

    # Create a copy of the given map and modify it instead
    top_tracks_to_recommendations_copy = copy.deepcopy(top_tracks_to_recommendations)

    _adjust_ratings_based_on_playcounts(top_tracks_to_recommendations_copy)

    if prefer_unheard_artists:
        _adjust_ratings_based_on_recent_artists(
            top_tracks_to_recommendations_copy, user, api_key
        )

    logging.info("Finished adjusting ratings")
    return _extract_tracks_from_map(top_tracks_to_recommendations_copy)


def _adjust_ratings_based_on_playcounts(top_tracks_to_recommendations):
    """Adjust rating based on associated top track's playcount; the thought being that recommendations based on more listened-to
    tracks should have a higher chance of being recommended"""
    for top_track in top_tracks_to_recommendations:
        recommendations = top_tracks_to_recommendations[top_track]
        for recommendation in recommendations:
            recommendation.recommendation_rating *= top_track.playcount


def _adjust_ratings_based_on_recent_artists(
    top_tracks_to_recommendations, user, api_key
):
    """Reduces tracks ratings based on their artists' playcount in the user's library"""
    recent_artists = fetch_recent_artists(user, api_key)
    for top_track in top_tracks_to_recommendations:
        recommendations = top_tracks_to_recommendations[top_track]
        for recommendation in recommendations:
            for artist in recent_artists:
                if recommendation.artist.lower() == artist.artist_name.lower():
                    # Reduce the rating by dividing it by the artist's playcount; the thought being that the more listened-to an artist is,
                    # the less chance there should be of one of their tracks being recommended
                    recommendation.recommendation_rating /= artist.playcount
                    logging.debug(
                        "Calculated rating for "
                        + str(recommendation)
                        + ": "
                        + str(recommendation.recommendation_rating)
                    )


def _extract_tracks_from_map(top_tracks_to_recommendations):
    all_recommendations = []
    for top_track in top_tracks_to_recommendations:
        recommendations = top_tracks_to_recommendations[top_track]
        all_recommendations = all_recommendations + recommendations
    return all_recommendations
