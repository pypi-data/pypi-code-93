from beartype.roar._roarexc import (
    BeartypeCallHintPepParamException,
)
from picsellia.pxl_exceptions import TyperError
from functools import wraps
import time


def exception_handler(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BeartypeCallHintPepParamException as exc:
            exc = str(exc).split('@beartyped ')
            message = exc[1]
            raise TypeError(message)
    return inner


def retry(exceptions, total_tries=4, initial_wait=0.5, backoff_factor=2):
    """
    calling the decorated function applying an exponential backoff.
    Args:
        exceptions: Exeption(s) that trigger a retry, can be a tuple
        total_tries: Total tries
        initial_wait: Time to first retry
        backoff_factor: Backoff multiplier (e.g. value of 2 will double the delay each retry).
        logger: logger to be used, if none specified print
    """
    def retry_decorator(f):
        @wraps(f)
        def func_with_retries(*args, **kwargs):
            _tries, _delay = total_tries + 1, initial_wait
            while _tries > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:
                    _tries -= 1
                    print_args = args if args else 'no args'
                    if _tries == 1:
                        raise
                    time.sleep(_delay)
                    _delay *= backoff_factor
                
        return func_with_retries
    return retry_decorator
