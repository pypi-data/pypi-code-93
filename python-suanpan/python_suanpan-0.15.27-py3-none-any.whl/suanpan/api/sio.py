# coding=utf-8
from __future__ import absolute_import, print_function

import time
import socketio

from suanpan.api import auth


def sio(*args, **kwargs):
    retryMaxTimes = kwargs.pop("retryMaxTimes", 30)
    retryDelay = kwargs.pop("retryDelay", 0.1)
    namespace = kwargs.get("namespaces")
    ctx = dict(connected=False)
    kwargs["headers"] = {**auth.defaultHeaders(), **kwargs.pop("headers", {})}
    client = socketio.Client()
    client.on("connect", handler=lambda: ctx.update(connected=True), namespace=namespace)
    client.connect(*args, **kwargs)
    if retryMaxTimes:
        for _ in range(retryMaxTimes):
            if ctx.get("connected", False):
                break
            time.sleep(retryDelay)
        else:
            if not ctx.get("connected", False):
                raise Exception("sio sonnected failed")
    return client
