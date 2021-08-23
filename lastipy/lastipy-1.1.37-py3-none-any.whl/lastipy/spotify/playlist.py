import logging
from lastipy.spotify.parse_spotify_tracks import parse_tracks
from lastipy.util.chunk import chunk_list

MAX_ITEMS_PER_REQUEST = 100


# TODO test
def get_tracks_in_playlists(spotify):
    """Returns all tracks in the currently-logged-in user's playlists"""

    logging.info(
        "Fetching all tracks in " + spotify.current_user()["id"] + "'s playlists"
    )

    playlists = spotify.current_user_playlists()["items"]

    tracks = []
    for playlist in playlists:
        tracks = tracks + get_tracks_in_playlist(spotify, playlist_id=playlist["id"])

    logging.info(
        "Fetched "
        + str(len(tracks))
        + " tracks in "
        + str(len(playlists))
        + " playlists"
    )
    logging.debug("Fetched tracks: " + str(tracks))

    return tracks


# TODO test
def replace_tracks_in_playlist(spotify, playlist_name, tracks):
    """Replaces all tracks in the currently-logged-in user's given playlist
    with the given tracks. If the playlist does not exist, creates it first."""

    logging.info(
        "Replacing "
        + str(len(tracks))
        + " tracks in "
        + spotify.current_user()["id"]
        + "'s playlist "
        + playlist_name
    )
    logging.debug("Replacing with tracks: " + str(tracks))

    playlist_id = _get_playlist(spotify, playlist_name)

    if playlist_id is None:
        playlist_id = _create_playlist(spotify, playlist_name)

    spotify.user_playlist_replace_tracks(
        user=spotify.current_user()["id"],
        playlist_id=playlist_id,
        tracks=[track.spotify_id for track in tracks],
    )

    logging.info("Finished replacing tracks")


# TODO test
def get_tracks_in_playlist(spotify, playlist_name=None, playlist_id=None):
    """Returns all tracks in the given user's given playlist"""

    if playlist_id is None:
        if playlist_name is not None:
            logging.info("Fetching tracks in playlist with name " + playlist_name)
            playlist_id = _get_playlist(spotify, playlist_name)
        else:
            raise Exception("playlist_name or playlist_id required")
    else:
        logging.info("Fetching tracks in playlist with ID " + playlist_id)

    tracks_in_playlist = []
    keep_fetching = True
    while keep_fetching:
        json_response = spotify.playlist_tracks(
            playlist_id=playlist_id, offset=len(tracks_in_playlist)
        )
        if json_response["items"]:
            tracks_in_playlist = tracks_in_playlist + parse_tracks(
                json_response["items"]
            )
        else:
            keep_fetching = False

    logging.info("Fetched " + str(len(tracks_in_playlist)) + " tracks")
    logging.debug("Fetched tracks: " + str(tracks_in_playlist))

    return tracks_in_playlist


# TODO test
def add_tracks_to_playlist(spotify, playlist_name, tracks):
    playlist_id = _get_playlist(spotify, playlist_name)

    if playlist_id is None:
        playlist_id = _create_playlist(spotify, playlist_name)

    logging.info(
        "Adding "
        + str(len(tracks))
        + " tracks to "
        + spotify.current_user()["id"]
        + "'s playlist "
        + playlist_name
    )
    logging.debug("Adding tracks: " + str(tracks))

    tracks_chunked = chunk_list(tracks, MAX_ITEMS_PER_REQUEST)
    for chunk in tracks_chunked:
        # Remove any tracks that don't have a Spotify ID
        chunk = [track for track in chunk if track.spotify_id is not None]
        if len(chunk) > 0:
            spotify.user_playlist_add_tracks(
                user=spotify.current_user()["id"],
                playlist_id=playlist_id,
                tracks=[track.spotify_id for track in chunk],
            )
        else:
            logging.debug("Chunk is empty, not adding any tracks")

    logging.info("Finished adding tracks")


# TODO test
def remove_tracks_from_playlist(spotify, playlist_name, tracks):
    logging.info(
        "Removing "
        + str(len(tracks))
        + " tracks from "
        + spotify.current_user()["id"]
        + "'s playlist "
        + playlist_name
    )
    logging.debug("Removing tracks: " + str(tracks))

    playlist_id = _get_playlist(spotify, playlist_name)

    if playlist_id is None:
        playlist_id = _create_playlist(spotify, playlist_name)

    tracks_chunked = chunk_list(tracks, MAX_ITEMS_PER_REQUEST)
    for chunk in tracks_chunked:
        # Remove any tracks that don't have a Spotify ID
        chunk = [track for track in chunk if track.spotify_id is not None]
        if len(chunk) > 0:
            spotify.user_playlist_remove_all_occurrences_of_tracks(
                user=spotify.current_user()["id"],
                playlist_id=playlist_id,
                tracks=[track.spotify_id for track in chunk],
            )
        else:
            logging.debug("Chunk is empty, not removing any tracks")

    logging.debug("Finished removing tracks")


def _create_playlist(spotify, playlist_name):
    logging.info("Creating playlist " + playlist_name)
    return spotify.user_playlist_create(
        user=spotify.current_user()["id"], name=playlist_name
    )["id"]


def _get_playlist(spotify, playlist_name):
    logging.debug("Looking for playlist " + playlist_name)
    playlists = spotify.current_user_playlists()
    playlists = [
        playlist for playlist in playlists["items"] if playlist["name"] == playlist_name
    ]
    if playlists:
        return playlists[0]["id"]
    else:
        return None
