from contextlib import contextmanager
from rich.console import Console
from time import time
from datetime import timezone

BEAT_TIME = 0.02


@contextmanager
def beat(console: Console, length: int = 1) -> None:
    with console:
        console.clear()
        yield
    time.sleep(length * BEAT_TIME)


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

def local_to_utc(local_dt):
    pass