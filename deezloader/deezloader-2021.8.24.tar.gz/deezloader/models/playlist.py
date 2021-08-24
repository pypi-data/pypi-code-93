#!/usr/bin/python3

from .track import Track

class Playlist:
	def __init__(self) -> None:
		self.__t_list = []
		self.zip_path = None

	@property
	def tracks(self) -> list[Track]:
		return self.__t_list