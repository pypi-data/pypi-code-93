import logging
import spotipy
from lastipy.spotify import token
from lastipy.spotify.parse_spotify_tracks import parse_tracks
import json


# TODO test
def search_for_tracks(spotify, query):
    """Returns a list of tracks for the given query"""

    logging.info("Searching in Spotify with query " + query)

    json_response = spotify.search(q=query)
    logging.debug(
        "All search results for query " + query + ": " + json.dumps(json_response)
    )

    converted_tracks = []
    if json_response["tracks"]:
        converted_tracks = parse_tracks(json_response["tracks"]["items"])
    logging.info(
        "Found "
        + str(len(converted_tracks))
        + " tracks for search query "
        + query
        + " in Spotify"
    )
    logging.debug("Found tracks: " + str(converted_tracks))
    return converted_tracks
