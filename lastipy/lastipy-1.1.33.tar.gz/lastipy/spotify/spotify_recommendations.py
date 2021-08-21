import logging
from lastipy.spotify.search import search_for_tracks
from lastipy.recommendations.recommended_track import RecommendedTrack

# TODO test
def fetch_recommendations(spotify, track, limit):
    logging.info(
        "Fetching up to "
        + str(limit)
        + " recommendations based on "
        + str(track)
        + " in Spotify"
    )
    track_in_spotify = search_for_tracks(
        spotify=spotify, query=track.artist + " " + track.track_name
    )[0]
    # TODO this accepts up to 5 tracks, so this could be more sophisticated by using multiple top-listened-to tracks in a single call
    recommendations = spotify.recommendations(
        seed_tracks=[track_in_spotify.spotify_id], limit=limit
    )

    parsed_recommendations = []
    for recommendation in recommendations["tracks"]:
        parsed_recommendations.append(
            RecommendedTrack(
                track_name=recommendation["name"],
                artist=recommendation["artists"][0]["name"],
                spotify_id=recommendation["id"],
                recommendation_rating=1,
            )
        )

    logging.info(
        "Fetched " + str(len(parsed_recommendations)) + " track recommendations"
    )
    return parsed_recommendations
