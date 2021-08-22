import logging
from lastipy.lastfm.library import period
from lastipy.lastfm.parse_lastfm_tracks import parse_track_name, parse_artist
from lastipy.lastfm.library.top_track import TopTrack
from lastipy.lastfm.library.paginated_endpoint import fetch_paginated_response

URL = "http://ws.audioscrobbler.com/2.0/?method=user.gettoptracks"


def fetch_top_tracks(user, api_key, a_period=period.OVERALL):
    """Fetches the top tracks for the given user over the given period"""

    logging.info("Fetching top tracks for user " + user + " over period " + a_period)

    paginated_json_responses = fetch_paginated_response(
        URL, user, api_key, "toptracks", [{"key": "period", "value": a_period}]
    )

    top_tracks = []
    for json_response in paginated_json_responses:
        for track in json_response["toptracks"]["track"]:
            top_tracks.append(
                TopTrack(
                    parse_track_name(track),
                    parse_artist(track),
                    int(track["playcount"]),
                )
            )

    # Filter out tracks with a playcount of 1, since those really shouldn't be considered "top"
    top_tracks = [track for track in top_tracks if track.playcount > 1]

    logging.info("Fetched " + str(len(top_tracks)) + " top tracks")
    logging.debug("Fetched tracks: " + str(top_tracks))
    return top_tracks
