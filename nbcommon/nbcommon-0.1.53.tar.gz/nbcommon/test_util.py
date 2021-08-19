import pytest
import asyncio
from . import util


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


def test_table_split_exception(event_loop):
    vertical = [1, 2]
    horizontal = [3, 4]

    def func(vertial, horizontal):
        raise Exception('who cares')

    exp = False
    try:
        event_loop.run_until_complete(util.table_split(vertical, horizontal, func))
    except Exception as e:
        print(f'exception: {e}')
        exp = True
    assert exp


def test_table_split_basic(event_loop):
    vertical = [1, 2]
    horizontal = [3, 4]

    def func(vertial, horizontal):
        r = [[0 for j in range(0, len(horizontal))] for i in range(0, len(vertical))]
        for i in range(0, len(vertical)):
            for j in range(0, len(horizontal)):
                r[i][j] = vertical[i] * horizontal[j]
        return r
    result = event_loop.run_until_complete(util.table_split(vertical, horizontal, func))
    assert len(result) == len(vertical)
    assert len(result[0]) == len(horizontal)
    assert result[0][0] == 3
    assert result[0][1] == 4
    assert result[1][0] == 6
    assert result[1][1] == 8


def test_table_split_large(event_loop):
    vertical = [i for i in range(0, 404)]
    horizontal = [i for i in range(0, 404)]

    async def func(v, h):
        r = [[0 for j in range(0, len(h))] for i in range(0, len(v))]
        for i in range(0, len(v)):
            for j in range(0, len(h)):
                r[i][j] = v[i] * h[j]
        return r
    result = event_loop.run_until_complete(util.table_split(vertical, horizontal, func))
    assert len(result) == len(vertical)
    assert len(result[0]) == len(horizontal)
    for i in range(0, len(vertical)):
        for j in range(0, len(horizontal)):
            assert result[i][j] == vertical[i] * horizontal[j]
