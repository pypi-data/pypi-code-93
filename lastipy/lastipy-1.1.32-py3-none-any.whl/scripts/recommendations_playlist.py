#!/usr/bin/env python3.7

from configparser import ConfigParser
import argparse
import os
from lastipy import definitions
from lastipy.lastfm.library import period
from lastipy.track import Track
from lastipy.util.setup_logging import setup_logging
import logging
from lastipy.util.parse_api_keys import ApiKeysParser
from spotipy import Spotify
from lastipy.spotify import token
from lastipy.recommendations.recommendations import generate_recommendations
from lastipy.spotify import playlist, search
from numpy.random import choice


# TODO test
def build_recommendations_playlist():
    """Adds recommendations to the given Spotify user's playlist based on the given Last.fm user's recommendations"""

    setup_logging("recommendations.log")
    args = _extract_args()

    spotify = Spotify(
        auth=token.get_token(
            args.spotify_user,
            args.spotify_client_id_key,
            args.spotify_client_secret_key,
        )
    )

    recommendations = generate_recommendations(
        lastfm_user=args.lastfm_user,
        lastfm_api_key=args.lastfm_api_key,
        spotify=spotify,
        recommendation_services=args.recommendation_services,
        recommendation_period=args.recommendation_period,
        max_recommendations_per_top_track=args.max_recommendations_per_top_track,
        blacklisted_artists=args.blacklisted_artists,
        prefer_unheard_artists=args.prefer_unheard_artists,
    )

    logging.info("Generating recommendations playlist...")
    tracks_for_playlist = []
    while len(tracks_for_playlist) < args.playlist_size and len(recommendations) > 0:
        # Find and remove the recommendation from the list using a random choice, weighted based on the recommendation's rating value
        recommendation = choice(
            recommendations, p=_calculate_rating_weights(recommendations)
        )
        recommendations.remove(recommendation)

        if recommendation.spotify_id is None:
            # If we didn't get the recommendation directly from Spotify, we need to get the ID from there before we can add to the playlist
            search_results = search.search_for_tracks(
                spotify=spotify,
                query=recommendation.artist + " " + recommendation.track_name,
            )
            if search_results and Track.are_equivalent(
                recommendation, search_results[0]
            ):
                recommendation.spotify_id = search_results[0].spotify_id

        if recommendation.spotify_id is not None and not any(
            recommendation.artist == item.artist for item in tracks_for_playlist
        ):
            logging.info("Adding " + str(recommendation))
            tracks_for_playlist.append(recommendation)

    playlist.replace_tracks_in_playlist(
        spotify, args.playlist_name, tracks_for_playlist
    )

    logging.info("Done!")


def _calculate_rating_weights(recommendations):
    logging.debug("Calculating recommendation rating weights")
    total_ratings = 0
    for recommendation in recommendations:
        total_ratings += recommendation.recommendation_rating

    rating_weights = []
    for recommendation in recommendations:
        rating_weights.append(recommendation.recommendation_rating / total_ratings)
    return rating_weights


def _extract_args():
    args_parser = _setup_args_parser()
    args = args_parser.parse_args()
    args = _extract_user_configs(args)
    args = _extract_api_keys(args)
    return args


def _setup_args_parser():
    parser = argparse.ArgumentParser(
        description="Create a Spotify playlist based off recommendations from Last.fm"
    )
    parser.add_argument(
        "user_configs_file", type=argparse.FileType("r", encoding="UTF-8")
    )
    parser.add_argument("api_keys_file", type=argparse.FileType("r", encoding="UTF-8"))
    return parser


def _extract_user_configs(args):
    config_parser = ConfigParser()
    config_parser.read(args.user_configs_file.name)
    section = "Config"
    args.lastfm_user = config_parser[section]["LastFMUser"]
    args.spotify_user = config_parser[section]["SpotifyUser"]
    args.recommendation_services = config_parser[section][
        "RecommendationServices"
    ].split(",")
    args.recommendation_period = config_parser[section]["RecommendationPeriod"]
    args.max_recommendations_per_top_track = int(
        config_parser[section]["MaxRecommendationsPerTopTrack"]
    )
    args.playlist_size = int(config_parser[section]["PlaylistSize"])
    args.playlist_name = config_parser[section]["PlaylistName"]
    args.blacklisted_artists = config_parser[section]["BlacklistedArtists"].split(",")
    args.prefer_unheard_artists = _str_to_bool(
        config_parser[section]["PreferUnheardArtists"]
    )
    return args


def _str_to_bool(to_convert):
    return to_convert == "True"


def _extract_api_keys(args):
    keys_parser = ApiKeysParser(args.api_keys_file)
    args.lastfm_api_key = keys_parser.lastfm_api_key
    args.spotify_client_id_key = keys_parser.spotify_client_id_key
    args.spotify_client_secret_key = keys_parser.spotify_client_secret_key
    return args


if __name__ == "__main__":
    build_recommendations_playlist()
