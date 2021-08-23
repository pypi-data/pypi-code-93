from itertools import zip_longest
import json
from plmbr.pipe import pipe
from plmbr.pipes import *


class validate(Pipe):
    def __init__(self, *vals):
        self.vals = vals

    def pipe(self, items: Iterator) -> Iterator:
        for expected, actual in zip_longest(self.vals, items):
            print(f'expecting {expected} got {actual}')
            assert actual == expected
            yield actual


def test_null(): (
    range(3)
    - null()
    > validate(0, 1, 2))


def test_json_loads():
    items = [{'a': 2}, {'b': 4}]
    (
        (json.dumps(i) for i in items)
        - json_loads()
        > validate(*items))


def test_json_dumps():
    items = [{'a': 2}, {'b': 4}]
    (
        items
        - json_dumps()
        > validate(*[json.dumps(i) for i in items]))


def test_batch():
    (
        range(3)
        - batch(batch_size=2)
        > validate([0, 1], [2]))

    (
        [0, 1, 2]
        - batch(batch_size=2)
        > validate([0, 1], [2]))


def test_unbatch(): (
    [range(2), range(3)]
    - unbatch()
    > validate(0, 1, 0, 1, 2))


def test_to(): (
    range(3)
    - to(lambda i: i + 1)
    > validate(1, 2, 3))


def test_keep(): (
    range(3)
    - keep(lambda i: i > 0)
    > validate(1, 2))


def test_drop_fields(): (
    ({'a': i, 'b': i, 'c': i} for i in range(3))
    - drop_fields('b', 'c')
    > validate({'a': 0}, {'a': 1}, {'a': 2}))


def test_uniq(): (
    ({'a': 0, 'b': i // 2, 'c': i} for i in range(3))
    - uniq('a', 'b')
    > validate(
        {'a': 0, 'b': 0, 'c': 0},
        {'a': 0, 'b': 1, 'c': 2}))


def test_sample(): (
    range(10)
    - sample(prob=.5)
    > validate(1, 4, 8, 9))


def test_window():
    (
        range(4)
        - window(size=2)
        > validate((0, 1), (1, 2), (2, 3)))

    (
        [0, 1, 2, 3]
        - window(size=2)
        > validate((0, 1), (1, 2), (2, 3)))


def test_append():
    res = [8]
    (
        range(4)
        > append(res)
    )
    assert res == [8, 0, 1, 2, 3]


def test_tee(): (
    [1, 2, 3]
    - tee(
        keep(lambda i: i < 3)
        - to(lambda i: i * 2),

        to(lambda i: i * 10))
    > validate(2, 4, 10, 20, 30))


def test_catch():
    class bad_pipe(Pipe):
        def pipe(self, items):
            for i in items:
                if i % 2:
                    self.throw(i)
                else:
                    yield i

    err = []

    (
        range(5)
        - bad_pipe()
        - validate(0, 2, 4)
        > catch(lambda i: err.append(i))
    )

    assert err == [1, 3]


def test_lambda():
    res = []
    (
        range(3)
        - to(lambda x: x + 1)
        - (lambda es: (e + 1 for e in es))
        > (lambda es: [res.append(e) for e in es])
    )

    assert res == [2, 3, 4]
