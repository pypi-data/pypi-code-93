#!/usr/bin/python3

from spotipy import Spotify
from .exceptions import InvalidLink
from spotipy.exceptions import SpotifyException
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2 import SpotifyClientCredentials

from .__others_settings__ import (
	spotify_client_id, spotify_client_secret
)

class Spo:
	def __generate_token(self):
		return SpotifyClientCredentials(
			client_id = spotify_client_id,
			client_secret = spotify_client_secret,
			cache_handler = CacheFileHandler(".cache_spoty_token"),
		)

	def __init__(self):
		self.__error_codes = [404, 400]

		self.__api = Spotify(
			client_credentials_manager = self.__generate_token()
		)

	def __lazy(self, results):
		albums = results['items']

		while results['next']:
			results = self.__api.next(results)
			albums.extend(results['items'])

		return results

	def get_track(self, ids):
		try:
			track_json = self.__api.track(ids)
		except SpotifyException as error:
			if error.http_status in self.__error_codes:
				raise InvalidLink(ids)

		return track_json

	def get_album(self, ids):
		try:
			album_json = self.__api.album(ids)
		except SpotifyException as error:
			if error.http_status in self.__error_codes:
				raise InvalidLink(ids)

		tracks = album_json['tracks']
		self.__lazy(tracks)
		return album_json

	def get_playlist(self, ids):
		try:
			playlist_json = self.__api.playlist(ids)
		except SpotifyException as error:
			if error.http_status in self.__error_codes:
				raise InvalidLink(ids)

		tracks = playlist_json['tracks']
		self.__lazy(tracks)
		return playlist_json

	def search(self, query):
		search = self.__api.search(query)
		return search