import logging
import os
import traceback
from typing import Collection, Iterable


def short_exception_logger(exc_info, *_):
    """
    Display excpetion traceback in concise one-line format.
    Avoid printing long, superfluous lines of traceback, especially for multi-cause exceptions.
    """
    try:
        ex_type, ex, tb = exc_info

        traceback_ex = traceback.TracebackException(type(ex_type), ex, tb, limit=None)
        lines = list(_get_traceback_lines(traceback_ex))
        tb = ','.join(lines)
        cause = _root_cause_type(ex)

        logging.error(f'{str(ex).strip()}: cause={cause}, traceback={tb}')
    except BaseException as e:
        logging.exception(e)


def _root_cause_type(e: BaseException) -> str:
    while e.__cause__ is not None:
        e = e.__cause__
    return type(e).__name__


def log_exception(e: BaseException):
    """
    Log exception in concise one-line format containing message, exception type and short traceback
    """
    exc_info = (type(e), e, e.__traceback__)
    short_exception_logger(exc_info)


def _get_traceback_lines(t1: traceback.TracebackException) -> Iterable[str]:
    while True:
        frames: Collection[traceback.FrameSummary] = t1.stack
        for frame in frames:
            yield f'{os.path.normpath(frame.filename)}:{frame.lineno}'

        if t1.__cause__ is None:
            break
        t1 = t1.__cause__
