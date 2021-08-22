import platform
from datetime import date
from typing import List, Optional
from urllib.parse import urlencode

import requests

from serifan import __version__, comics_list, exceptions

from .utils import list_strings_to_dates


class Session:
    """
    Session to request api endpoints
    """

    def __init__(self) -> None:
        self.header = {
            "User-Agent": f"Serifan/{__version__} ({platform.system()}; {platform.release()})"
        }
        self.api_url = "https://api.shortboxed.com/comics/v1/{}"

    def call(self, endpoint, params=None):
        """
        Method to make request for api endpoints.
        :param str endpoint: The endpoint to request information from.
        :param dict params: Parameters to add to the request.
        """
        params = {} if params is None else urlencode(params)
        url = self.api_url.format("/".join(str(e) for e in endpoint))

        try:
            response = requests.get(url, params=params, headers=self.header)
        except requests.exceptions.ConnectionError as e:
            raise exceptions.ApiError("Connection error: {}".format(repr(e)))

        return response.json()

    def new_releases(self) -> comics_list.ComicsList:
        """
        Method to request a list of this weeks current new release comics.

        :return: A list of :class:`Comic` objects.
        :rtype: ComicsList
        """
        return comics_list.ComicsList(self.call(["new"], params={}))

    def previous_releases(self) -> comics_list.ComicsList:
        """
        Method to request a list of the previous weeks released comics.

        :return: A list of :class:`Comic` objects.
        :rtype: ComicsList
        """
        return comics_list.ComicsList(self.call(["previous"], params={}))

    def future_releases(self) -> comics_list.ComicsList:
        """
        Method to request a list of the next weeks comics.

        :return: A list of :class:`Comic` objects.
        :rtype: ComicsList
        """
        return comics_list.ComicsList(self.call(["future"], params={}))

    def release_date(self, release_date: str) -> comics_list.ComicsList:
        """
        Method to request comics with a specific release date.

        :param release_date: Date comics where released in iso8601 format (ie: 2016-02-17).
        :type params: str

        :return: A list of :class:`Comic` objects.
        :rtype: ComicsList
        """
        return comics_list.ComicsList(self.call(["release_date", release_date], params={}))

    def available_release_dates(self) -> List[date]:
        """
        Method to retrieve list of release dates.
        """
        return list_strings_to_dates(self.call(["releases", "available"]))

    def query(
        self,
        publisher: Optional[str] = None,
        title: Optional[str] = None,
        creators: Optional[str] = None,
        release_date: Optional[str] = None,
    ) -> comics_list.ComicsList:
        """
        Method to search for a list of comics.

        :param publisher: Publisher to search by.
        :type params: str, optional

        :param title: Title to search for.
        :type params: str, optional

        :param creators: Creator to search for.
        :type params: str, optional

        :param release_date: Date comics where released in iso8601 format (ie: 2016-02-17).
        :type params: str, optional

        :return: A list of :class:`Comic` objects.
        :rtype: ComicsList
        """
        params = {}
        if publisher:
            params["publisher"] = publisher
        if title:
            params["title"] = title
        if creators:
            params["creators"] = creators
        if release_date:
            params["release_date"] = release_date

        return comics_list.ComicsList(self.call(["query"], params=params))
