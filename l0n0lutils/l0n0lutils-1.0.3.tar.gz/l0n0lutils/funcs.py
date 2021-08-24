import asyncio
import hashlib
import random
import string
from typing import Callable


def md5(data):
    if isinstance(data, str):
        data = data.encode()
    return hashlib.md5(data).hexdigest()


def random_string(slen=10):
    letters = string.ascii_letters \
        + string.digits  \
        + string.whitespace  \
        + string.punctuation
    return ''.join(random.sample(letters, slen))


def ok(data: dict):
    return "OK" == data["errMsg"] \
        or "Ok" == data["errMsg"] \
        or "oK" == data["errMsg"] \
        or "ok" == data["errMsg"]


on_closes = []

def on_close_function(fn:Callable):
    on_closes.append(fn)
    return fn


def asyncio_run_forever(loop: asyncio.BaseEventLoop = None):
    loop = loop or asyncio.get_event_loop()
    try:
        print("Press Ctrl+C to Close.")
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        for fn in on_closes:
            fn()

        for task in asyncio.all_tasks(loop):
            task.cancel()
            try:
                loop.run_until_complete(task)
            except asyncio.CancelledError:
                pass
            
        loop.stop()
        loop.close()
