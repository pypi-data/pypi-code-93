from lastipy.spotify.parse_spotify_tracks import parse_tracks
from lastipy.spotify.playlist import get_tracks_in_playlist
import spotipy
import logging
from lastipy.util.chunk import chunk_list

MAX_ITEMS_PER_REQUEST = 50


def get_saved_tracks(spotify):
    """Returns the current logged-in users's saved tracks (Liked Songs)"""

    logging.info("Fetching " + spotify.current_user()["id"] + "'s saved tracks")

    saved_tracks = []
    keep_fetching = True
    while keep_fetching:
        json_response = spotify.current_user_saved_tracks(offset=len(saved_tracks))
        if json_response["items"]:
            saved_tracks = saved_tracks + parse_tracks(json_response["items"])
        else:
            keep_fetching = False

    logging.info("Fetched " + str(len(saved_tracks)) + " saved tracks")
    logging.debug("Fetched tracks: " + str(saved_tracks))

    return saved_tracks


def add_tracks_to_library(spotify, tracks):
    """Adds the given tracks to the current logged-in user's saved tracks (Liked Songs)"""

    logging.info(
        "Adding "
        + str(len(tracks))
        + " to "
        + spotify.current_user()["id"]
        + "'s library"
    )
    logging.debug("Adding tracks: " + str(tracks))
    track_chunks = chunk_list(tracks, MAX_ITEMS_PER_REQUEST)
    for chunk in track_chunks:
        spotify.current_user_saved_tracks_add([track.spotify_id for track in chunk])
    logging.info("Finished adding tracks")


def add_albums_to_library(spotify, albums):
    """Adds the given albums to the current logged-in user's library"""

    logging.info(
        "Adding "
        + str(len(albums))
        + " to "
        + spotify.current_user()["id"]
        + "'s library"
    )
    logging.debug("Adding albums: " + str(albums))
    album_chunks = chunk_list(albums, MAX_ITEMS_PER_REQUEST)
    for chunk in album_chunks:
        spotify.current_user_saved_albums_add([album.spotify_id for album in chunk])
    logging.info("Finished adding albums")


# TODO test
def remove_tracks_from_library(spotify, tracks):
    """Removes the given tracks from the current logged-in user's saved tracks (Liked Songs)"""

    logging.info(
        "Removing "
        + str(len(tracks))
        + " from "
        + spotify.current_user()["id"]
        + "'s library"
    )
    logging.debug("Removing tracks: " + str(tracks))
    track_chunks = chunk_list(tracks, MAX_ITEMS_PER_REQUEST)
    for chunk in track_chunks:
        spotify.current_user_saved_tracks_delete([track.spotify_id for track in chunk])
    logging.info("Finished removing tracks")
