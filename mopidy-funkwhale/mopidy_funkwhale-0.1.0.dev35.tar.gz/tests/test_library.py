import pytest
import time
import uuid
from mopidy import models

import mopidy_funkwhale.library

from . import factories


def test_convert_artist_to_model():
    payload = {"id": 42, "mbid": str(uuid.uuid4()), "name": "Test artist"}

    result = mopidy_funkwhale.library.convert_to_artist(payload)

    assert type(result) == models.Artist
    assert result.musicbrainz_id == payload["mbid"]
    assert result.uri == "funkwhale:artists:%s" % (payload["id"],)
    assert result.name == payload["name"]
    assert result.sortname == payload["name"]


def test_convert_album_to_model():
    payload = {
        "id": 3,
        "tracks": [1, 2, 3, 4],
        "mbid": str(uuid.uuid4()),
        "title": "Test album",
        "artist": {"id": 42, "mbid": str(uuid.uuid4()), "name": "Test artist"},
        "release_date": "2017-01-01",
        "cover": {
            "original": "/media/albums/covers/2018/10/03/b4e94b07e-da27-4df4-ae2a-d924a9448544.jpg"
        },
    }

    result = mopidy_funkwhale.library.convert_to_album(payload)

    assert type(result) == models.Album
    assert result.musicbrainz_id == payload["mbid"]
    assert result.uri == "funkwhale:albums:%s" % (payload["id"],)
    assert result.name == payload["title"]
    assert result.date == payload["release_date"]
    assert result.num_tracks == len(payload["tracks"])
    assert result.artists == frozenset(
        [mopidy_funkwhale.library.convert_to_artist(payload["artist"])]
    )


def test_convert_track_to_model():
    payload = {
        "id": 2,
        "title": "Test track",
        "mbid": str(uuid.uuid4()),
        "creation_date": "2017-01-01",
        "position": 12,
        "artist": {"id": 43, "mbid": str(uuid.uuid4()), "name": "Test artist 2"},
        "album": {
            "id": 3,
            "tracks": [1, 2, 3, 4],
            "mbid": str(uuid.uuid4()),
            "title": "Test album",
            "artist": {"id": 42, "mbid": str(uuid.uuid4()), "name": "Test artist"},
            "release_date": "2017-01-01",
            "cover": {
                "original": "/media/albums/covers/2018/10/03/b4e94b07e-da27-4df4-ae2a-d924a9448544.jpg"
            },
        },
        "uploads": [{"bitrate": 128000, "duration": 120}],
    }

    result = mopidy_funkwhale.library.convert_to_track(payload)

    assert type(result) == models.Track
    assert result.musicbrainz_id == payload["mbid"]
    assert result.uri == "funkwhale:tracks:%s" % (payload["id"],)
    assert result.name == payload["title"]
    assert result.date == payload["album"]["release_date"]
    assert result.length == payload["uploads"][0]["duration"] * 1000
    assert result.bitrate == payload["uploads"][0]["bitrate"] / 1000

    assert result.album == mopidy_funkwhale.library.convert_to_album(payload["album"])
    assert result.artists == frozenset(
        [mopidy_funkwhale.library.convert_to_artist(payload["artist"])]
    )


@pytest.mark.parametrize(
    "uri, expected",
    [
        ("funkwhale:albums:42", ("album", 42)),
        ("funkwhale:tracks:42", ("track", 42)),
        ("funkwhale:artists:42", ("artist", 42)),
    ],
)
def test_parse_uri(uri, expected):
    assert mopidy_funkwhale.library.parse_uri(uri) == expected


@pytest.mark.parametrize("type", ["track", "album", "artist"])
def test_to_ref(type):
    obj = getattr(models, type.capitalize())(uri="hello:world", name="Hello")
    expected = getattr(models.Ref, type)(uri=obj.uri, name=obj.name)
    assert mopidy_funkwhale.library.to_ref(obj) == expected


@pytest.mark.parametrize(
    "path, expected_handler,remaining",
    [
        ("funkwhale:directory:favorites", "browse_favorites", []),
        ("funkwhale:directory:favorites:by-date", "browse_favorites", ["by-date"]),
    ],
)
def test_browse_routing(library, path, expected_handler, mocker, remaining):
    handler = mocker.patch.object(
        library, expected_handler, return_value=("test", False)
    )

    assert library.browse(path) == "test"
    assert handler.called_once_with(remaining)


def test_browse_favorites_root(library):
    expected = (
        [
            models.Ref.directory(
                uri="funkwhale:directory:favorites:recent", name="Recent"
            ),
            # models.Ref.directory(
            #     uri="funkwhale:directory:favorites:by-artist", name="By artist"
            # ),
        ],
        False,
    )
    assert library.browse_favorites([]) == expected


def test_browse_favorites_recent(library, client, requests_mock):
    track = factories.TrackJSONFactory()
    url = (
        client.session.url_base
        + "tracks/?favorites=true&page_size=50&&ordering=-creation_date"
    )
    requests_mock.get(url, json={"results": [track]})

    expected = [mopidy_funkwhale.library.convert_to_track(track, ref=True)], True
    result = library.browse_favorites(["recent"])

    assert result == expected


def test_browse_artists_root(library):
    expected = (
        [
            models.Ref.directory(
                uri="funkwhale:directory:artists:recent", name="Recent"
            ),
            models.Ref.directory(
                uri="funkwhale:directory:artists:by-name", name="By name"
            ),
            models.Ref.directory(
                uri="funkwhale:directory:artists:scope-me", name="Own Content"
            ),
        ],
        False,
    )
    assert library.browse_artists([]) == expected


def test_browse_artists_recent(client, library, requests_mock):
    artist1 = factories.ArtistJSONFactory()
    artist2 = factories.ArtistJSONFactory()
    url = (
        client.session.url_base
        + "artists/?page_size=50&ordering=-creation_date&playable=true"
    )
    requests_mock.get(url, json={"results": [artist1, artist2]})
    uri_prefix = "funkwhale:directory:artists:recent"

    expected = (
        [
            mopidy_funkwhale.library.convert_to_artist(
                artist1, uri_prefix=uri_prefix, ref=True
            ),
            mopidy_funkwhale.library.convert_to_artist(
                artist2, uri_prefix=uri_prefix, ref=True
            ),
        ],
        True,
    )
    assert library.browse_artists(["recent"]) == expected


def test_browse_artists_albums(client, library, requests_mock):
    album1 = factories.AlbumJSONFactory()
    album2 = factories.AlbumJSONFactory(artist=album1["artist"])
    url = (
        client.session.url_base
        + "albums/?ordering=title&page_size=50&playable=true&artist=%s"
        % album1["artist"]["id"]
    )
    requests_mock.get(url, json={"results": [album1, album2]})
    uri_prefix = "funkwhale:directory:artists:by-name:%s" % album1["artist"]["id"]
    expected = (
        [
            mopidy_funkwhale.library.convert_to_album(
                album1, uri_prefix=uri_prefix, ref=True
            ),
            mopidy_funkwhale.library.convert_to_album(
                album2, uri_prefix=uri_prefix, ref=True
            ),
        ],
        True,
    )
    assert library.browse_artists(["by-name", album1["artist"]["id"]]) == expected


def test_browse_artists_album_single(client, library, requests_mock):
    track = factories.TrackJSONFactory()
    url = (
        client.session.url_base
        + "tracks/?page_size=50&ordering=position&playable=true&album="
        + str(track["album"]["id"])
    )
    requests_mock.get(url, json={"results": [track]})
    expected = ([mopidy_funkwhale.library.convert_to_track(track, ref=True)], True)
    assert (
        library.browse_artists(
            ["by-name", track["album"]["artist"]["id"], track["album"]["id"]]
        )
        == expected
    )


def test_cache_set():
    cache = mopidy_funkwhale.library.Cache()
    cache.set("hello:world", "value")
    assert cache["hello:world"][0] < time.time()
    assert cache["hello:world"][1] == "value"


def test_cache_get():
    cache = mopidy_funkwhale.library.Cache()
    cache["hello:world"] = (time.time(), "value")
    assert cache.get("hello:world") == "value"


def test_cache_key_too_old():
    cache = mopidy_funkwhale.library.Cache(max_age=60)
    t = time.time() - 60
    cache["hello:world"] = (t, "value")
    assert cache.get("hello:world") is None
    assert "hello:world" not in cache


def test_lookup_from_cache(library):
    track = object()
    library.cache.set("funkwhale:artists:42", track)

    result = library.lookup("funkwhale:artists:42")
    assert result == [track]


def test_lookup_from_cache_iterable(library):
    track = [object()]
    library.cache.set("funkwhale:artists:42", track)

    result = library.lookup("funkwhale:artists:42")
    assert result == track
