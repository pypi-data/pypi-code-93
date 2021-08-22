##
#  File:  TimeoutMultiProc.py
#  Date:  17-Nov-2011  Jdw
#
##

"""
Code to timeout with processes.

>>> @timeout(.5)
... def sleep(x):
...     print "ABOUT TO SLEEP {0} SECONDS".format(x)
...     time.sleep(x)
...     return x

>>> sleep(1)
Traceback (most recent call last):
   ...
TimeoutException: timed out after 0 seconds

>>> sleep(.2)
0.2

>>> @timeout(.5)
... def exc():
...     raise Exception('Houston we have problems!')

>>> exc()
Traceback (most recent call last):
   ...
Exception: Houston we have problems!

"""
import multiprocessing
import time

# import logging
import signal
from functools import wraps


class TimeoutException(Exception):
    def __init__(self, value):
        super(TimeoutException, self).__init__(value)

        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return repr(self.value)


class RunableProcessing(multiprocessing.Process):  # pragma: no cover
    def __init__(self, func, *args, **kwargs):
        self.queue = multiprocessing.Queue(maxsize=1)
        args = (func,) + args
        multiprocessing.Process.__init__(self, target=self.run_func, args=args, kwargs=kwargs)
        # logger = multiprocessing.log_to_stderr()
        # logger.setLevel(logging.INFO)

    def run_func(self, func, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
            self.queue.put((True, result))
        except Exception as e:
            self.queue.put((False, e))

    def done(self):
        return self.queue.full()

    def result(self):
        return self.queue.get()


def timeout(seconds, message="Function call timed out"):
    def wrapper(function):
        def _handleTimeout(signum, frame):
            raise TimeoutException(message)

        @wraps(function)
        def wrapped(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handleTimeout)
            signal.alarm(seconds)
            try:
                result = function(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapped

    return wrapper


def timeoutMp(seconds, force_kill=True):  # pragma: no cover
    def wrapper(function):
        @wraps(function)
        def inner(*args, **kwargs):
            now = time.time()
            proc = RunableProcessing(function, *args, **kwargs)
            proc.start()
            proc.join(seconds)
            if proc.is_alive():
                if force_kill:
                    proc.terminate()
                runtime = int(time.time() - now)
                raise TimeoutException("timed out after {0} seconds".format(runtime))
            assert proc.done()
            success, result = proc.result()
            if success:
                return result
            else:
                raise result

        return inner

    return wrapper


if __name__ == "__main__":  # pragma: no cover
    import doctest

    doctest.testmod()
