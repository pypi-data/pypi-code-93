import logging
from lastipy.lastfm.parse_lastfm_tracks import parse_artist, parse_track_name
from lastipy.track import Track
from lastipy.lastfm.library.paginated_endpoint import fetch_paginated_response

URL = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks"


def fetch_recent_tracks(user, api_key):
    """Fetches recent tracks for the given user"""

    logging.info("Fetching recent tracks for " + user)

    paginated_json_responses = fetch_paginated_response(
        URL, user, api_key, "recenttracks"
    )
    recent_tracks = []
    for json_response in paginated_json_responses:
        for track in json_response["recenttracks"]["track"]:
            recent_tracks.append(Track(parse_track_name(track), parse_artist(track)))

    logging.info("Fetched " + str(len(recent_tracks)) + " recent tracks")
    logging.debug("Fetched tracks: " + str(recent_tracks))
    return recent_tracks
