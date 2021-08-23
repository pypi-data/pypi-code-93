from abc import abstractmethod
from typing import Callable, Iterator, List, Union


class Handler:
    catch: Union[None, Callable] = None

    def throw(self, e: Exception):
        if self.catch:
            self.catch(e)
        else:
            print(e)


def set_handler(*hs: Handler):
    for h1, h2 in zip(hs[:-1], hs[1:]):
        if not h1.catch:
            h1.catch = h2.throw

    return h2


class Tap(Handler):
    def __init__(self, action):
        self.action = action

    def __sub__(self, p):
        return set_handler(self, p, Tap(lambda: p(self())))

    def __gt__(self, p):
        for _ in set_handler(self, p, self - p)():
            pass

    def __call__(self):
        return self.action()


class Pipe(Handler):
    def __sub__(self, p):
        return set_handler(self, p, pipe(lambda it: p(self(it))))

    def __rsub__(self, it):
        return set_handler(self, Tap(lambda: self(it)))

    def __lt__(self, it):
        Tap(lambda: it) > self

    def __call__(self, it):
        return self.pipe(it)

    @ abstractmethod
    def pipe(self, it: Iterator) -> Iterator: ...


class pipe(Pipe):
    def __init__(self, action):
        self.action = action

    def pipe(self, it):
        return self.action(it)
