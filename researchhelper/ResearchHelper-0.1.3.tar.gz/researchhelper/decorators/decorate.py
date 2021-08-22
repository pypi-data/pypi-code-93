"""In this file we hold all useful decorators that we develop over time.

For hints check:
https://betterprogramming.pub/python-decorators-5-advanced-features-to-know-17dd9be7517b
"""

from functools import wraps
import time


def logging_time(unit):
    """Decorate inner function and log time.

    Parameters
    ----------
    func : Function
        Decorate function such that it prints the elapsed runtime.
    unit : str
        Time constant in which you want to see how long the operation took.

    Returns
    -------
    logger : Inner function of the wrapper.

    """
    def logger(func):
        @wraps(func)
        def inner_logger(*args, **kwargs):
            """Log time."""
            start = time.time()
            func(*args, **kwargs)
            if unit == "ms":
                scaling = 1000
            elif unit == "m":
                scaling = 1/60
            else:
                scaling = 1
            print(f"Calling {func.__name__}: {(time.time() - start) * scaling:.5f} {unit}")

        return inner_logger

    return logger


if __name__ == "__main__":

    @logging_time("s")
    def sleep():
        """Sleep."""
        time.sleep(3)

    @logging_time("ms")
    def sleep2():
        """Sleep."""
        time.sleep(2.1)

    print("sleep")
    sleep()
    print("sleep2")
    sleep2()
