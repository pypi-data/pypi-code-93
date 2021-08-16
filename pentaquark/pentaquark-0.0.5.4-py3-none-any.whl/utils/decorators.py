import time
import logging

logger = logging.getLogger(__name__)


def log_time(func):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        res = func(*args, **kwargs)
        t2 = time.time()
        logger.debug(f"TIMING - {res.__name__}: {t2 - t1:2.5f} (seconds)")
        return res
    return wrapper
