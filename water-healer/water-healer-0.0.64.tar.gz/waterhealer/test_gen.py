from tornado import gen
import asyncio
from datetime import datetime
import time


@gen.coroutine
def plus(x):
    print(datetime.now())
    time.sleep(1)
    return x + 1


@gen.coroutine
def loop():
    r = yield [plus(1), plus(1), plus(1)]
    return r


r = loop().result()
print(r)
