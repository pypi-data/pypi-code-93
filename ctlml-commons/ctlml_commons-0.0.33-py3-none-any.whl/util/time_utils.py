import logging
import time
from functools import wraps

from ctlml_commons.util.constants import ACCESS_LOG_NAME


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        start = time.time()
        result = f(*args, **kw)
        end = time.time()

        logging.getLogger(ACCESS_LOG_NAME).info(f"{f.__name__} - args: {args}, kw: {kw} - {end - start}")

        return result

    return wrap
