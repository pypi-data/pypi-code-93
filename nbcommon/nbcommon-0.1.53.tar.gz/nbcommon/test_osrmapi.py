from .osrmapi import NearestResponse, RouteResponse, TableResponse, MatchResponse, parse_google_coords, LatLng
from .osrmapi import API
from . import aiorequests
import pytest
import asyncio


def test_parse_google_coords():
    a = parse_google_coords('1,2|3,4|5,6')
    assert len(a) == 3
    assert a[0] == LatLng(lat=1, lng=2)
    assert a[1] == LatLng(lat=3, lng=4)
    assert a[2] == LatLng(lat=5, lng=6)

    b = parse_google_coords('1,2')
    assert len(b) == 1
    assert b[0] == LatLng(lat=1, lng=2)


def test_nearest_response():
    mock = {
        'code': 'Ok',
        'waypoints': [
            {
                'hint': '',
                'distance': 1.0,
                'name': 'whocares',
                'location': [1.0, 2.0],
                'nodes':[1, 20],
            },
        ],
    }
    NearestResponse(**mock)


def test_route_response():
    mock = {
        'code': 'Ok',
        'routes': [
            {
                'geometry': 'whocares',
                'distance': 1.0,
                'duration': 1.0,
                'legs': [
                    {
                        'distance': 1.0,
                        'duration': 1.0,
                        'steps': [
                            {
                                'geometry': 'whocares2',
                            }
                        ],
                    },
                ],
            },
            {
                'geometry': 'whocares',
                'distance': 2.0,
                'duration': 2.0,
                'legs': [
                    {
                        'distance': 2.0,
                        'duration': 2.0,
                        'steps': [
                            {
                                'geometry': 'whocares2',
                            }
                        ],
                    },
                ],
            },
        ],
    }
    r = RouteResponse(**mock)
    assert r.routes[0].geometry == 'whocares'
    assert r.routes[0].legs[0].steps[0].geometry == 'whocares2'
    assert r.routes[1].geometry == 'whocares'
    assert r.routes[1].legs[0].steps[0].geometry == 'whocares2'


def test_table_response():
    mock = {
        'code': 'Ok',
        'sources': [
            {
                'name': 'whocares',
                'location': [1.0, 2.0],
                'hint': '',
                'distance': 0.1,
            },
        ],
        'destinations': [
            {
                'name': 'whocares',
                'location': [1.0, 2.0],
                'hint': '',
                'distance': 0.1,
            },
        ],
        'durations': [
            [
                1.0,
            ],
        ],
        'distances': [
            [
                1.0,
            ],
        ],
    }
    TableResponse(**mock)


def test_match_response():
    mock = {
        'code': 'Ok',
        'tracepoints': [
            {
                'matchings_index': 1,
                'location': [1.0, 2.0],
            },
        ],
        'matchings': [
            {
                'distance': 1.0,
            },
        ],
    }
    MatchResponse(**mock)


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


async def mock_route(url):
    return {
        'code': 'Ok'
    }


def test_route(monkeypatch, event_loop):
    api = API('whocares')
    monkeypatch.setattr(aiorequests, 'http_get_json', mock_route)
    coords = [LatLng(lat=1, lng=2)]
    result = event_loop.run_until_complete(api.route(coords, 'json'))

    assert type(result) == RouteResponse

    exp = False
    try:
        event_loop.run_until_complete(api.route(coords, 'whocares'))
    except Exception as e:
        print(f'exception: {e}')
        exp = True
    assert exp
