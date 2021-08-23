"""
A collection of reusable pipes.
"""
from collections import deque
from plmbr.pipe import Pipe
from typing import Callable, Dict, Iterator
import json
from tqdm import tqdm
import random
import itertools


class null(Pipe):
    def pipe(self, items: Iterator) -> Iterator:
        return items


class json_loads(Pipe):
    def pipe(self, items: Iterator) -> Iterator:
        for item in items:
            try:
                yield json.loads(item)
            except Exception as e:
                self.throw(e)


class json_dumps(Pipe):
    def pipe(self, items: Iterator) -> Iterator:
        return (json.dumps(item) for item in items)


class batch(Pipe):
    def __init__(self, batch_size=64) -> None:
        self.batch_size = batch_size

    def pipe(self, it: Iterator) -> Iterator:
        batch = []
        for i in it:
            batch.append(i)
            if len(batch) == self.batch_size:
                yield batch
                batch = []

        if batch:
            yield batch


class unbatch(Pipe):
    def pipe(self, lists: Iterator) -> Iterator:
        return (item for l in lists for item in l)


class progress(Pipe):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def pipe(self, it: Iterator) -> Iterator:
        return iter(tqdm(it, **self.kwargs))


class to(Pipe):
    def __init__(self, f: Callable):
        self.f = f

    def pipe(self, items: Iterator) -> Iterator:
        for item in items:
            try:
                yield self.f(item)
            except Exception as e:
                self.throw(e)


class keep(Pipe):
    def __init__(self, filter):
        self.filter = filter

    def pipe(self, items: Iterator) -> Iterator:
        for item in items:
            try:
                if self.filter(item):
                    yield item
            except Exception as e:
                self.throw(e)


class drop_fields(Pipe):
    def __init__(self, *fields: str):
        self.fields = fields

    def pipe(self, items: Iterator[Dict]) -> Iterator[Dict]:
        for item in items:
            try:
                for field in self.fields:
                    del item[field]

                yield item
            except Exception as e:
                self.throw(e)


class uniq(Pipe):
    def __init__(self, *fields: str):
        self.fields = fields
        self.set: set = set()

    def pipe(self, items: Iterator[Dict]) -> Iterator[Dict]:
        for item in items:
            i = frozenset({field: item[field] for field in self.fields}.items())
            if i in self.set:
                continue

            self.set.add(i)
            yield item


class sample(Pipe):
    def __init__(self, prob, seed=2020):
        self.prob = prob
        self.seed = seed

    def pipe(self, items: Iterator[Dict]) -> Iterator[Dict]:
        random.seed(self.seed)
        for item in items:
            if random.uniform(0, 1) < self.prob:
                yield item


class window(Pipe):
    def __init__(self, size):
        self.size = size
        self.window = deque([])

    def pipe(self, it: Iterator) -> Iterator[tuple]:
        for e in it:
            self.window.append(e)
            if len(self.window) == self.size:
                yield tuple(self.window)
                self.window.popleft()


class log(Pipe):
    def pipe(self, items: Iterator) -> Iterator:
        for item in items:
            print(item)
            yield item


class save(Pipe):
    def __init__(self, file) -> None:
        self.file = file

    def pipe(self, items: Iterator):
        with open(self.file, 'w') as f:
            for item in items:
                print(item, file=f)
                yield item


class append(Pipe):
    def __init__(self, to) -> None:
        self.to = to

    def pipe(self, items: Iterator):
        for item in items:
            self.to.append(item)
            yield item


class tee(Pipe):
    def __init__(self, *pipes) -> None:
        self.pipes = pipes

    def pipe(self, items: Iterator) -> Iterator:
        for items in (
                pipe(items)
                for items, pipe
                in zip(itertools.tee(items, len(self.pipes)), self.pipes)):
            for item in items:
                yield item


class catch(Pipe):
    def __init__(self, catch=None):
        print(catch)
        self.catch = catch or (lambda e: print(e))

    def pipe(self, it: Iterator) -> Iterator:
        return it
