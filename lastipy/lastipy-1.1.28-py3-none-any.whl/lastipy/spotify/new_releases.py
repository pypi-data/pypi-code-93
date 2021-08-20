import spotipy
from lastipy.spotify.parse_spotify_tracks import parse_tracks
from lastipy.spotify.library import get_saved_tracks
from lastipy.spotify.playlist import get_tracks_in_playlists
from datetime import datetime
import logging
from lastipy.track import Track
from lastipy.spotify import album
from lastipy.util.filter import filter_out_duplicates, filter_out_tracks_in_second_list


# TODO test
def fetch_new_tracks(
    spotify,
    album_types=[album.SINGLE_ALBUM_TYPE, album.ALBUM_ALBUM_TYPE],
    ignore_remixes=False,
    ignore_songs_in_library=True,
    as_of_date=datetime.today().date(),
):
    """Fetches new tracks (as of the given date) released by the current Spotify user's followed artists"""

    logging.info(
        "Fetching new tracks for "
        + spotify.current_user()["id"]
        + " as of "
        + str(as_of_date)
    )

    new_albums = fetch_new_albums(spotify, album_types, as_of_date)

    all_tracks = []
    for album in new_albums:
        all_tracks += _fetch_album_tracks(spotify, album)

    new_tracks = parse_tracks(all_tracks)
    new_tracks = filter_out_duplicates(new_tracks)

    if ignore_remixes:
        logging.info("Filtering out those pesky remixes...")
        new_tracks = [
            track for track in new_tracks if "remix" not in track.track_name.lower()
        ]

    if ignore_songs_in_library:
        logging.info(
            "Filtering out tracks that are already in the user's saved tracks and playlists..."
        )
        saved_tracks = get_saved_tracks(spotify)
        new_tracks = filter_out_tracks_in_second_list(new_tracks, saved_tracks)

        playlist_tracks = get_tracks_in_playlists(spotify)
        new_tracks = filter_out_tracks_in_second_list(new_tracks, playlist_tracks)

    logging.info("Fetched " + str(len(new_tracks)) + " new tracks " + str(new_tracks))
    return new_tracks


# TODO test
def fetch_new_albums(
    spotify,
    album_types=[album.SINGLE_ALBUM_TYPE, album.ALBUM_ALBUM_TYPE],
    as_of_date=datetime.today().date(),
):
    """Fetches new albums (as of the given date) released by the given Spotify user's followed artists"""

    followed_artist_ids = _fetch_followed_artists(spotify)

    logging.info(
        "Fetching new albums for "
        + spotify.current_user()["id"]
        + " as of "
        + str(as_of_date)
    )

    all_albums = []
    for artist_id in followed_artist_ids:
        artist_albums = _fetch_artist_albums(spotify, album_types, artist_id)
        all_albums += artist_albums

    # TODO remove this once https://github.com/evanjamesjackson/lastipy/issues/22 is fixed...
    logging.info(
        "Before filtering by date, fetched " + str(len(all_albums)) + " albums"
    )
    logging.info(str(all_albums))

    new_albums = _filter_new_albums(all_albums, as_of_date)

    logging.info("Fetched " + str(len(new_albums)) + " new albums " + str(new_albums))
    return new_albums


def _fetch_followed_artists(spotify):
    followed_artists = []

    curr_response = spotify.current_user_followed_artists(limit=50)

    while len(curr_response["artists"]["items"]) > 0:
        curr_response = spotify.current_user_followed_artists(
            limit=50,
            after=curr_response["artists"]["items"][len(curr_response) - 1]["id"],
        )
        followed_artists += curr_response["artists"]["items"]

    # The above Spotipy function doesn't really seem to function properly and results in duplicates,
    # so we remove them here by converting the list to just the IDs (not doing so results in
    # an unhashable error), then converting to a set and back to a list
    followed_artists = [artist["id"] for artist in followed_artists]
    followed_artist_ids = list(set(followed_artists))
    return followed_artist_ids


def _filter_new_albums(all_albums, as_of_date):
    new_albums = []
    for album in all_albums:
        if album.release_date_precision == "day":
            if datetime.strptime(album.release_date, "%Y-%m-%d").date() == as_of_date:
                new_albums.append(album)
        else:
            logging.warn(
                "Album release date precision is not 'day' so ignoring (album: "
                + str(album)
                + ")"
            )
    return new_albums


def _fetch_artist_albums(spotify, album_types, artist_id):
    albums = []
    for album_type in album_types:
        curr_response = spotify.artist_albums(
            artist_id, album_type=album_type, limit=50
        )
        albums += _convert_albums(curr_response)
        while len(curr_response["items"]) > 0:
            curr_response = spotify.artist_albums(
                artist_id, album_type=album_type, limit=50, offset=len(albums)
            )
            albums += _convert_albums(curr_response)
    return albums


def _convert_albums(json_album_response):
    return [
        album.SpotifyAlbum(
            name=item["name"],
            artist=item["artists"][0]["name"],
            album_type=item["album_type"],
            spotify_id=item["id"],
            release_date_precision=item["release_date_precision"],
            release_date=item["release_date"],
        )
        for item in json_album_response["items"]
    ]


def _fetch_album_tracks(spotify, album):
    curr_response = spotify.album_tracks(album.spotify_id, limit=50)
    album_tracks = curr_response["items"]
    while len(curr_response["items"]) > 0:
        curr_response = spotify.album_tracks(
            album.spotify_id, limit=50, offset=len(album_tracks)
        )
        album_tracks += curr_response["items"]
    return album_tracks
