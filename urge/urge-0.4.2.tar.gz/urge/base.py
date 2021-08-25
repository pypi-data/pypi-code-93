import time
import copy
import typing as t
import schedule as sche
from functools import wraps
from .utils import convert_time, callable_check, drop


class Action:

    # procs: t.Sequence[t.Callable]
    procs: t.Union[t.List, "ProcManager"]

    def once(self):
        ret = self._excute()
        return ret

    def every(self, freq) -> None:
        # shoud be in convert_time ?
        if isinstance(freq, dict):
            freq = convert_time(freq)

        sche.every(freq).seconds.do(self.once)

    def when(self, time: str):
        sche.every().day.at(time).do(self.once)

    def _excute(self):
        if not self.procs:
            raise Exception()
        elif isinstance(self.procs, list):
            self.procs = ProcManager(*self.procs)

        seed = copy.deepcopy(self.__dict__)
        seed = drop(seed, ["procs", "self"])
        # little dangerous here drop self only use key-name,
        # think about if I use 'this' instead of 'self' wow...
        ret = self.procs.excute(seed)
        # ret = self.procs(seed)
        # ret = self.procs(self.__dict__)
        # DONE Need change procs() -> procs.excute() -> way better
        return ret


class ProcManager:
    def __init__(self, *procs) -> None:
        map(callable_check, procs)
        # self._procs += procs -> Because instances share their class _proc
        self._procs = procs

    def __iter__(self) -> t.Callable:
        for f in self._procs:
            yield f

    def __add__(self, other):
        _new_procs = self._procs + other._procs
        return ProcManager(*_new_procs)

    def __call__(self, seed):
        ret = self.pipe(seed, *self._procs)
        return ret

    def excute(self, seed):
        ret = self.pipe(seed, *self._procs)
        return ret

    def pipe(self, seed, *funcs) -> t.Any:

        for func in funcs:
            if isinstance(seed, dict):
                seed = func(**seed)
                continue
            seed = func(seed)
        return seed

    # @staticmethod
    # def pipe(seed, *funcs)->t.Any:
    #     for func in funcs:
    #         if isinstance(seed, dict):
    #             seed = func(**seed)
    #             continue
    #         seed = func(seed)
    #     return seed


class action(Action):
    def __init__(self, procs: t.List) -> None:
        self.procs = procs

    def __call__(self, decorated):
        # TODO really need a smarter way to detect self, and get result from procs
        @wraps(decorated)
        def instead(*args, **kwd):
            # print("Inside decotrator")
            # print(args, kwd)
            seed = decorated(*args, **kwd)  # when decorate a method, self in args...
            self.__dict__.update(seed)
            return self

        return instead


def require():
    pass


def start():
    while True:
        time.sleep(1)
        sche.run_pending()
