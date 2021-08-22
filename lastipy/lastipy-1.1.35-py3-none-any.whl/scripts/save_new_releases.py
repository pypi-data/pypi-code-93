#!/usr/bin/env python3.7

from configparser import ConfigParser
import argparse
import os
from lastipy import definitions
from lastipy.lastfm.library.top_tracks import fetch_top_tracks
from lastipy.lastfm.library.recent_tracks import fetch_recent_tracks
from lastipy.lastfm.library.recent_artists import fetch_recent_artists
from lastipy.util.filter import filter_out_tracks_in_second_list
from lastipy.lastfm.library import period
from lastipy.spotify import playlist, search, library
from lastipy.track import Track
from numpy.random import choice
from spotipy import Spotify
from lastipy.spotify import token
from lastipy.util.setup_logging import setup_logging
import logging
from lastipy.spotify import new_releases
from datetime import datetime
from lastipy.util.parse_api_keys import ApiKeysParser
from lastipy.spotify import album
from datetime import date, timedelta


# TODO test
def save_new_releases():
    """Saves all new releases released yesterday by the specified Spotify user's followed artists to their library. We check
    for yesterday so that all releases released throughout that day are picked up (trying to get today's releases has a chance of missing anything
    released after this script is run)."""

    setup_logging("new_releases.log")

    args = _extract_args()

    spotify = Spotify(
        auth=token.get_token(
            args.spotify_user,
            args.spotify_client_id_key,
            args.spotify_client_secret_key,
        )
    )

    yesterday = date.today() - timedelta(days=1)

    if args.save_albums_to_liked_songs:
        _save_new_tracks(
            spotify,
            args.lastfm_user,
            args.lastfm_api_key,
            args.ignore_remixes,
            args.ignore_scrobbled_songs,
            yesterday,
            # Save all types of albums straight to Liked Songs
            [album.SINGLE_ALBUM_TYPE, album.ALBUM_ALBUM_TYPE],
        )
    else:
        _save_new_tracks(
            spotify,
            args.lastfm_user,
            args.lastfm_api_key,
            args.ignore_remixes,
            args.ignore_scrobbled_songs,
            yesterday,
            # Save only single-type albums to Liked Songs
            [album.SINGLE_ALBUM_TYPE],
        )

        new_albums = new_releases.fetch_new_albums(
            spotify, album_types=[album.ALBUM_ALBUM_TYPE], as_of_date=yesterday
        )
        if len(new_albums) > 0:
            library.add_albums_to_library(spotify, new_albums)
        else:
            logging.info("No new albums to add!")

    logging.info("Done!")


def _save_new_tracks(
    spotify,
    lastfm_user,
    lastfm_api_key,
    ignore_remixes,
    ignore_scrobbled_songs,
    as_of_date,
    album_types,
):
    new_tracks = new_releases.fetch_new_tracks(
        spotify,
        ignore_remixes=ignore_remixes,
        album_types=album_types,
        as_of_date=as_of_date,
    )

    if ignore_scrobbled_songs:
        logging.info("Filtering out scrobbled tracks from new releases")
        # TODO this is pretty inefficient but it appears to be the only way to tell if a user has scrobbled a track
        recent_tracks = fetch_recent_tracks(user=lastfm_user, api_key=lastfm_api_key)
        new_tracks = filter_out_tracks_in_second_list(new_tracks, recent_tracks)

    if len(new_tracks) > 0:
        library.add_tracks_to_library(spotify, new_tracks)
    else:
        logging.info("No tracks to add!")


def _extract_args():
    args = _parse_args()
    _extract_api_keys(args)
    _extract_user_configs(args)
    return args


def _extract_api_keys(args):
    keys_parser = ApiKeysParser(args.api_keys_file)
    args.spotify_client_id_key = keys_parser.spotify_client_id_key
    args.spotify_client_secret_key = keys_parser.spotify_client_secret_key
    args.lastfm_api_key = keys_parser.lastfm_api_key


def _extract_user_configs(args):
    config_parser = ConfigParser()
    config_parser.read(args.user_configs_file.name)
    section = "Config"
    args.spotify_user = config_parser.get(section, "SpotifyUser")
    args.lastfm_user = config_parser.get(section, "LastFMUser")
    args.ignore_remixes = config_parser.getboolean(section, "IgnoreRemixes")
    args.ignore_scrobbled_songs = config_parser.getboolean(
        section, "IgnoreScrobbledSongs"
    )
    args.save_albums_to_liked_songs = config_parser.getboolean(
        section, "SaveAlbumsToLikedSongs"
    )
    return args


def _parse_args():
    args_parser = argparse.ArgumentParser(
        description="Adds new tracks from the given user's followed artists to their saved/liked tracks"
    )
    args_parser.add_argument(
        "user_configs_file", type=argparse.FileType("r", encoding="UTF-8")
    )
    args_parser.add_argument(
        "api_keys_file", type=argparse.FileType("r", encoding="UTF-8")
    )
    return args_parser.parse_args()


if __name__ == "__main__":
    save_new_releases()
