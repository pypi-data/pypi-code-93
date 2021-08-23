import pytest


def test_client_search(client, requests_mock):
    requests_mock.get(
        client.session.url_base + "search?query=myquery", json={"hello": "world"}
    )

    result = client.search("myquery")
    assert result == {"hello": "world"}


def test_client_get_track(client, requests_mock):
    requests_mock.get(client.session.url_base + "tracks/12/", json={"hello": "world"})

    result = client.get_track(12)
    assert result == {"hello": "world"}


def test_client_list_tracks(client, requests_mock):
    requests_mock.get(
        client.session.url_base + "tracks/?artist=12", json={"hello": "world"}
    )

    result = client.list_tracks({"artist": 12})
    assert result == {"hello": "world"}


def test_client_list_artists(client, requests_mock):
    requests_mock.get(
        client.session.url_base + "artists/?playable=true", json={"hello": "world"}
    )

    result = client.list_artists({"playable": "true"})
    assert result == {"hello": "world"}


def test_client_list_albums(client, requests_mock):
    requests_mock.get(
        client.session.url_base + "albums/?playable=true", json={"hello": "world"}
    )

    result = client.list_albums({"playable": "true"})
    assert result == {"hello": "world"}


def test_load_all(client, requests_mock):
    page1 = {"results": [1, 2, 3], "next": "https://first.page"}
    page2 = {"results": [4, 5, 6], "next": "https://second.page"}
    page3 = {"results": [7, 8, 9], "next": None}
    requests_mock.get(page1["next"], json=page2)
    requests_mock.get(page2["next"], json=page3)
    assert (
        list(client.load_all(page1))
        == page1["results"] + page2["results"] + page3["results"]
    )
