import concurrent.futures
import os
import json
import queue
import threading
import urllib.request
from .LAUNCHER import Launcher
import logging.handlers
import logging
import multiprocessing
import traceback
import typing

ALL = [
    "JsonHandler",
    "Launcher",
    "LogHandler",
    "format_root",
    "DownloadFromJson",
    "callback_type",
    "ALL",
]

__all__ = ALL

callback_type = typing.Callable[[str, logging.LogRecord], None]


class JsonHandler:
    def __init__(self, file: typing.Optional[str] = None):
        self.file = file

    def load(self) -> dict:
        with open(self.file, 'r') as loaded:
            return json.load(loaded)

    def dump(self, store: dict) -> None:
        with open(self.file, 'w') as loaded:
            return json.dump(store, loaded, indent=4)

    def __call__(self, raw: str) -> dict:
        return json.loads(raw)

    def __str__(self) -> str:
        return self.file

    def parse_url(self, raw_link: str) -> dict:
        with urllib.request.urlopen(raw_link) as raw:
            return self(raw.read())

    def close(self) -> None:
        os.remove(self.file)


def format_root() -> logging.Logger:
    root = logging.getLogger("")
    root.setLevel(logging.DEBUG)

    root.addHandler(logging.StreamHandler(None)) if len(root.handlers) == 0 else None

    handler = root.handlers[0]
    handler.setLevel(logging.DEBUG)

    handler.setFormatter(
        logging.Formatter("%(asctime)s:[%(levelname)s]:%(threadName)s :: %(message)s", datefmt="%d-%m-%Y %I:%M:%S"
                          )
    )

    return root


class DownloadFromJson:
    def __init__(
            self, save, raw
    ):
        self.linear = queue.Queue()

        self._safe = threading.Lock()
        self.__, self.___ = 0, False
        # count: 0
        # traversal done ?

        self.linear.put(
            (raw, "")
        )
        # tree, rel_path

        self.pointer = save

        if not os.path.isdir(self.pointer):
            raise NotADirectoryError(f"{self.pointer} is not a directory")

        self.failed = False

    def initiate(self):
        while self.linear.qsize():
            for raw, rel in self.__arrange(*self.linear.get()):
                if not raw:
                    self._log("Downloading %s".format(rel))
                    continue

                self.linear.put(
                    (raw, rel)
                )

        with self._safe:
            self.___ = True
            if self.__ == 0 and self.___:
                self._done()
                self.___ = False

    def __arrange(self, tree, rel):
        for name in tree:
            _ = os.path.join(rel, name)
            __ = os.path.join(self.pointer, _)

            if type(tree[name]) == dict:
                None if os.path.exists(__) else os.mkdir(__)

                yield tree[name], _

            else:
                None if os.path.exists(__) else self._grab(tree[name], __)
                yield None, _

    def _grab(self, url, path):
        with self._safe:
            self.__ += 1

    def _parse(self, future: typing.Optional[concurrent.futures.Future]):
        with self._safe:
            self.__ -= 1
        return future

    def _log(self, txt):
        return txt

    def _done(self):
        pass


class LogHandler(logging.Handler):
    def __init__(
            self, level=logging.DEBUG, formatter=logging.Formatter(
                "%(asctime)s:[%(levelname)s]:%(threadName)s :: %(message)s", datefmt="%d-%m-%Y %I:%M:%S"
            ), emit_record: typing.Callable = None, emit_id: typing.Callable = None
    ):
        super().__init__(level)
        self._record, self._emit_id = emit_record, emit_id

        self.setFormatter(formatter)

    def register_callbacks(
            self, emit_record: typing.Callable = None, emit_id: typing.Callable = None
    ):
        self._record = emit_record if emit_record else self._record
        self._emit_id = emit_id if emit_id else self._emit_id

    def emit(self, record: logging.LogRecord):
        record = self.format(record)

        self._record(
            record
        ) if self._record else None

        return record
