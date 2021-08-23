from __future__ import unicode_literals

import collections
import logging
import re
import time
import urllib

from mopidy import backend, models

logger = logging.getLogger(__name__)


def generate_uri(path):
    return "funkwhale:directory:%s" % path


def new_folder(name, path):
    return models.Ref.directory(uri=generate_uri(path), name=name)


def simplify_search_query(query):

    if isinstance(query, dict):
        r = []
        for v in query.values():
            if isinstance(v, list):
                r.extend(v)
            else:
                r.append(v)
        return " ".join(r)
    if isinstance(query, list):
        return " ".join(query)
    else:
        return query


class Cache(collections.OrderedDict):
    def __init__(self, max_age=0):
        self.max_age = max_age
        super(Cache, self).__init__()

    def set(self, key, value):
        if self.max_age is None:
            return
        now = time.time()
        self[key] = (now, value)

    def get(self, key):
        if self.max_age is None:
            return
        value = super(Cache, self).get(key)
        if value is None:
            return
        now = time.time()
        t, v = value
        if self.max_age and t + self.max_age < now:
            # entry is too old, we delete it
            del self[key]
            return None
        return v


class FunkwhaleLibraryProvider(backend.LibraryProvider):
    root_directory = models.Ref.directory(uri="funkwhale:directory", name="Funkwhale")

    def __init__(self, *args, **kwargs):
        super(FunkwhaleLibraryProvider, self).__init__(*args, **kwargs)
        self.vfs = {"funkwhale:directory": collections.OrderedDict()}
        self.add_to_vfs(new_folder("Favorites", "favorites"))
        self.add_to_vfs(new_folder("Artists", "artists"))
        self.add_to_vfs(new_folder("Albums", "albums"))
        self.add_to_vfs(new_folder("Libraries", "libraries"))
        # self.add_to_vfs(new_folder('Following', ['following']))
        # self.add_to_vfs(new_folder('Sets', ['sets']))
        # self.add_to_vfs(new_folder('Stream', ['stream']))
        self.cache = Cache(max_age=self.backend.config["funkwhale"]["cache_duration"])

    def add_to_vfs(self, _model):
        self.vfs["funkwhale:directory"][_model.uri] = _model

    def browse(self, uri):
        cache_key = uri
        from_cache = self.cache.get(cache_key)
        if from_cache:
            try:
                len(from_cache)
                return from_cache
            except TypeError:
                return [from_cache]

        if not self.vfs.get(uri):
            if uri.startswith("funkwhale:directory:"):
                uri = uri.replace("funkwhale:directory:", "", 1)
            parts = uri.split(":")
            remaining = parts[1:] if len(parts) > 1 else []
            handler = getattr(self, "browse_%s" % parts[0])
            result, cache = handler(remaining)
            if cache:
                self.cache.set(cache_key, result)
            return result

        # root directory
        return list(self.vfs.get(uri, {}).values())

    def browse_favorites(self, remaining):
        if remaining == []:
            return (
                [
                    new_folder("Recent", "favorites:recent"),
                    # new_folder("By artist", "favorites:by-artist"),
                ],
                False,
            )

        if remaining == ["recent"]:
            payload = self.backend.client.list_tracks(
                {"favorites": "true", "ordering": "-creation_date", "page_size": 50}
            )
            tracks = [
                convert_to_track(row, ref=True, cache=self.cache)
                for row in self.backend.client.load_all(payload, max=10)
            ]
            return tracks, True
        return [], False

    def browse_albums(self, remaining, uri_prefix=""):
        logger.debug("Handling albums route: %s", remaining)
        if remaining == []:
            return (
                [
                    new_folder("Recent", "albums:recent"),
                    new_folder("By name", "albums:by-name"),
                    new_folder("Own Content", "albums:scope-me"),
                ],
                False,
            )

        if remaining == ["recent"]:
            # list recent albums
            payload = self.backend.client.list_albums(
                {"ordering": "-creation_date", "page_size": 50, "playable": "true"}
            )

            uri_prefix = "funkwhale:directory:albums:recent"
            albums = [
                convert_to_album(row, uri_prefix=uri_prefix, ref=True)
                for row in self.backend.client.load_all(payload, max=1)
            ]

            return albums, True

        if remaining == ["by-name"]:
            # list all albums sorted by name
            payload = self.backend.client.list_albums(
                {"ordering": "title", "page_size": 50, "playable": "true"}
            )

            uri_prefix = "funkwhale:directory:albums:by-name"
            albums = [
                convert_to_album(row, uri_prefix=uri_prefix, ref=True)
                for row in self.backend.client.load_all(payload)
            ]

            return albums, True

        if remaining == ["scope-me"]:
            # list all albums self uploaded
            payload = self.backend.client.list_albums(
                {"ordering": "title", "page_size": 50, "scope": "me"}
            )

            uri_prefix = "funkwhale:directory:albums:scope-me"
            albums = [
                convert_to_album(row, uri_prefix=uri_prefix, ref=True)
                for row in self.backend.client.load_all(payload)
            ]

            return albums, True

        if len(remaining) == 2:
            album = remaining[1]
            payload = self.backend.client.list_tracks(
                {
                    "ordering": "position",
                    "page_size": 50,
                    "playable": "true",
                    "album": album,
                }
            )
            tracks = [
                convert_to_track(row, ref=True, cache=self.cache)
                for row in self.backend.client.load_all(payload)
            ]
            return tracks, True
        else:
            artist, album = remaining[0], None
            payload = self.backend.client.list_albums(
                {
                    "ordering": "title",
                    "page_size": 50,
                    "playable": "true",
                    "artist": artist,
                }
            )
            albums = [
                convert_to_album(row, uri_prefix=uri_prefix, ref=True)
                for row in self.backend.client.load_all(payload)
            ]
            return albums, True

    def browse_artists(self, remaining):
        logger.debug("Handling artist route: %s", remaining)
        if remaining == []:
            return (
                [
                    new_folder("Recent", "artists:recent"),
                    new_folder("By name", "artists:by-name"),
                    new_folder("Own Content", "artists:scope-me"),
                ],
                False,
            )

        root = remaining[0]
        end = remaining[1:]
        albums_uri_prefix = "funkwhale:directory:artists:" + ":".join(
            [str(i) for i in remaining]
        )
        if root == "recent":
            if end:
                # list albums
                return self.browse_albums(uri_prefix=albums_uri_prefix, remaining=end)

            # list recent artists
            payload = self.backend.client.list_artists(
                {"ordering": "-creation_date", "page_size": 50, "playable": "true"}
            )
            uri_prefix = "funkwhale:directory:artists:recent"

            artists = [
                convert_to_artist(row, uri_prefix=uri_prefix, ref=True)
                for row in self.backend.client.load_all(payload, max=1)
            ]
            return artists, True

        if root == "by-name":
            if end:
                # list albums
                return self.browse_albums(uri_prefix=albums_uri_prefix, remaining=end)

            # list recent artists
            payload = self.backend.client.list_artists(
                {"ordering": "name", "page_size": 50, "playable": "true"}
            )
            uri_prefix = "funkwhale:directory:artists:by-name"
            artists = [
                convert_to_artist(row, uri_prefix=uri_prefix, ref=True)
                for row in self.backend.client.load_all(payload)
            ]
            return artists, True

        if root == "scope-me":
            if end:
                # list albums
                return self.browse_albums(uri_prefix=albums_uri_prefix, remaining=end)

            payload = self.backend.client.list_artists(
                {"ordering": "name", "page_size": 50, "scope": "me"}
            )
            uri_prefix = "funkwhale:directory:artists:scope-me"
            artists = [
                convert_to_artist(row, uri_prefix=uri_prefix, ref=True)
                for row in self.backend.client.load_all(payload)
            ]
            return artists, True

        if root == "by-library":
            logger.debug("Handling artists by lib route: %s", end)
            if len(end) == 1:
                payload = self.backend.client.list_artists(
                    {"ordering": "name", "page_size": 50, "library": end}
                )
                uri_prefix = "funkwhale:directory:artists:by-name"
                artists = [
                    convert_to_artist(row, uri_prefix=uri_prefix, ref=True)
                    for row in self.backend.client.load_all(payload)
                ]
                return artists, True

        return [], False

    def browse_libraries(self, remaining):
        logger.debug("Handling libraries route: %s", remaining)

        payload = self.backend.client.list_libraries(
             {"ordering": "name", "page_size": 50}
        )
        uri_prefix = "funkwhale:directory:artists:by-library"
        libraries = [
            convert_to_ref(row, uri_prefix=uri_prefix)
            for row in self.backend.client.load_all(payload)
        ]
        return libraries, True

    def get_images(self, uris):
        logger.debug("Handling get images: %s", uris)
        result = {}

        for uri in uris:
            track_id = uri.split(":")[-1]
            cache_key = "funkwhale:images:%s" % track_id
            from_cache = self.cache.get(cache_key)

            if from_cache:
                result[uri] = from_cache
                continue

            payload = self.backend.client.get_track(track_id)
            if not payload["album"]["cover"]:
                continue

            result[uri] = []

            for type, cover_url in payload["album"]["cover"]["urls"].items():
                if not cover_url:
                    continue

                if type == "large_square_crop":
                    image = models.Image(uri=cover_url, width=600, height=600)
                elif type == "medium_square_crop":
                    image = models.Image(uri=cover_url, width=200, height=200)
                else:
                    image = models.Image(uri=cover_url)

                result[uri].append(image)

            self.cache.set(cache_key, result[uri])

        return result

    def search(self, query=None, uris=None, exact=False):
        # TODO Support exact search
        if not query:
            return

        else:
            search_query = simplify_search_query(query)
            logger.info("Searching Funkwhale for: %s", search_query)
            raw_results = self.backend.client.search(search_query)
            artists = [convert_to_artist(row) for row in raw_results["artists"]]
            albums = [convert_to_album(row) for row in raw_results["albums"]]
            tracks = [convert_to_track(row) for row in raw_results["tracks"]]

            return models.SearchResult(
                uri="funkwhale:search", tracks=tracks, albums=albums, artists=artists
            )

    def lookup(self, uri):
        from_cache = self.cache.get(uri)
        if from_cache:
            try:
                len(from_cache)
                return from_cache
            except TypeError:
                return [from_cache]

        if "fw:" in uri:
            uri = uri.replace("fw:", "")
            return self.backend.remote.resolve_url(uri)

        client = self.backend.client
        config = {
            "track": lambda id: [client.get_track(id)],
            "album": lambda id: client.list_tracks({"album": id})["results"],
            "artist": lambda id: client.list_tracks({"artist": id})["results"],
        }

        try:
            type, id = parse_uri(uri)
        except (IndexError, ValueError):
            logger.info(f"Lookup failed: invalid uri '{uri}'")
            return []
        else:
            payload = config[type](id)
            return [convert_to_track(row, cache=self.cache) for row in payload]


def parse_uri(uri):
    uri = uri.replace("funkwhale:", "", 1)
    parts = uri.split(":")
    type = parts[0].rstrip("s")
    id = int(parts[1])
    return type, id


def cast_to_ref(f):
    def inner(payload, *args, **kwargs):
        ref = kwargs.pop("ref", False)
        cache = kwargs.pop("cache", None)
        result = f(payload, *args, **kwargs)
        if cache is not None:
            cache.set(result.uri, result)
        if ref:
            return to_ref(result)
        return result

    return inner


@cast_to_ref
def convert_to_artist(payload, uri_prefix="funkwhale:artists"):
    return models.Artist(
        uri=uri_prefix + ":%s" % payload["id"],
        name=payload["name"],
        sortname=payload["name"],
        musicbrainz_id=payload["mbid"],
    )


@cast_to_ref
def convert_to_album(payload, uri_prefix="funkwhale:albums"):
    artist = convert_to_artist(payload["artist"])
    return models.Album(
        uri=uri_prefix + ":%s" % payload["id"],
        name=payload["title"],
        musicbrainz_id=payload["mbid"],
        artists=[artist],
        date=payload["release_date"],
        num_tracks=len(payload.get("tracks", [])),
    )


@cast_to_ref
def convert_to_track(payload, uri_prefix="funkwhale:tracks"):
    artist = convert_to_artist(payload["artist"])
    album = convert_to_album(payload["album"])

    try:
        upload = payload["uploads"][0]
    except (KeyError, IndexError):
        upload = {}
    return models.Track(
        uri=uri_prefix + ":%s" % payload["id"],
        name=payload["title"],
        musicbrainz_id=payload["mbid"],
        artists=[artist],
        album=album,
        date=payload["album"]["release_date"],
        bitrate=int((upload.get("bitrate") or 0) / 1000),
        length=(upload.get("duration") or 0) * 1000,
        track_no=payload["position"],
    )


def convert_to_ref(payload, uri_prefix="funkwhale:libraries"):
    try:
        upload = payload["uploads"][0]
    except (KeyError, IndexError):
        upload = {}
    return models.Ref(
        uri=uri_prefix + ":%s" % payload["uuid"],
        name=payload["name"],
    )


def to_ref(obj):
    getter = getattr(models.Ref, obj.__class__.__name__.lower())
    return getter(uri=obj.uri, name=obj.name)
