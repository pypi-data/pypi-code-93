import os
import logging
import inspect
from functools import partial
import json
from urllib.parse import urljoin
import dataclasses
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from operator import contains

import requests


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


class DisplayMixin:
    def fields(self, includes=None, excludes=None):
        fields = self.__dataclass_fields__.keys()
        if includes:
            fields = filter(partial(contains, includes), fields)
        if excludes:
            fields = filter(lambda field: field not in excludes, fields)
        return [field for field in fields if field != "name"]

    def row(self, includes=None, excludes=None):
        field_names = self.fields(includes, excludes)
        return [self.name] + [getattr(self, field) for field in field_names]

    def to_dict(self):
        return dict(
            map(
                lambda kv: (
                    kv[0],
                    str(kv[1]) if isinstance(kv[1], datetime) else kv[1],
                ),
                dataclasses.asdict(self).items(),
            )
        )


@dataclass
class Source(DisplayMixin):
    """ Sources the api pulls from """

    # - A unique string id for the source.
    source_id: str
    # - The name of the source.
    name: str
    # - The state (abbreviated) the source is located in.
    state: str
    # - The state (full name) the source is located in.
    state_full: str
    # - A boolean value stating if mugshots are available for this source.
    has_mugshots: bool

    # Fields not mentioned in api docs
    city: str
    address1: str
    source_url: str
    county: str
    phone: str
    zip_code: str
    email: str


@dataclass
class Record(DisplayMixin):
    # - The name of the individual.
    name: str
    # - The image url of mugshot.
    mugshot: str
    # - A unique string id for the record.
    id: str
    # - Book Date string in YYYY-MM-DD format.
    book_date: datetime
    # - Book Date string in MMM DD, YYYY format.
    book_date_formatted: datetime
    # - A string array of charges.
    charges: List[str]
    # - The url on JailBase.com to get more info.
    more_info_url: str
    # - An array of details about the individual. Each array item is a two element array with the first index a description and the second index a value.
    details: Optional[List[str]] = None

    def __post_init__(self):
        self.book_date = datetime.strptime(self.book_date, "%Y-%m-%d")
        self.book_date_formatted = datetime.strptime(
            self.book_date_formatted, "%b %d, %Y"
        )


class JailBase:
    def __init__(
        self, base_url="http://www.JailBase.com/api/{version}", version=1, cache=None
    ):
        """
        parameters:
        cache -- directory name for cached results to be put
        """
        self.base_url = base_url.format(version=version).rstrip("/") + "/"
        self.cache = cache

        self.log = logging.getLogger(self.__class__.__name__)

    def _url(self, path):
        return urljoin(self.base_url, path) + "/"

    def _get(self, *args, **kwargs):
        resp = requests.get(*args, **kwargs)
        resp.raise_for_status()
        return resp.json()

    def _fetcher(self, *args, **kwargs):
        calling_func_name = inspect.stack()[1].function
        return partial(self._get, self._url(calling_func_name), *args, **kwargs)

    def _cache_or_get(self, fetcher, filename=None, cache=None):
        cache = cache if cache is not None else self.cache
        if cache:
            calling_func_name = inspect.stack()[1].function
            cache_folder = os.path.join(cache, calling_func_name)
            if not os.path.isdir(cache_folder):
                os.makedirs(cache_folder)

            cache_file = os.path.join(cache_folder, filename or "response.json")
            if os.path.isfile(cache_file):
                self.log.debug("Using cache %s", cache_file)
                with open(cache_file, "r") as fp:
                    return json.load(fp)

            server_result = fetcher()
            with open(cache_file, "w+") as fp:
                json.dump(server_result, fp)
            return server_result
        server_result = fetcher()
        return server_result

    def recent(self, source_id, cache=None):
        params = {"source_id": source_id}
        page = 1

        while page != 0:
            self.log.debug("recent %s page %d", source_id, page)
            data = self._cache_or_get(
                self._fetcher(params={**params, "page": page}),
                filename=f"{source_id}__{page}.json",
                cache=cache,
            )
            for record in data["records"]:
                yield Record(**record)
            page = data.get("next_page", 0)

        return data

    def sources(self, cache=None):
        """
        The sources this api pulls from.
        """

        data = self._cache_or_get(
            self._fetcher(), filename="sources.json", cache=cache,
        )
        records = data["records"]
        return [Source(**record) for record in records]
