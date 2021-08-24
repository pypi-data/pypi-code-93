# permutation, combination, print_fac, print_*, n'th fib

import ctypes as c
import os

_ = c.CDLL(os.path.join(os.path.dirname(__file__), "gmp.dylib"))

_.pfib.argtypes = (c.c_ulonglong,)

_.factorial.argtypes = (c.c_ulong,)
_.factorial.restype = c.c_char_p

_.fibonacci.argtypes = (c.c_ulong, c.c_ulong)
_.fibonacci.restype = c.c_char_p


def print_fib(term_count: int):
    '''prints fibonacci series up to term_count'''

    if not (isinstance(term_count, int) and term_count > 0):
        raise ValueError("'term_count' has to be bigger than 0 and 'int'.")

    _.pfib(term_count)


def factorial(term: int) -> int:
    '''prints the factorial of `term`.'''

    if not (isinstance(term, int) and term >= 0):
        raise ValueError("'term' has to be bigger than 0 and 'int'.")

    _result = _.factorial(term)
    result = _result.value
    _.free(_result)

    return result


def fibonacci(term: int, precision: int = 1000) -> int:
    '''prints the term'th term of the fibonacci serie.'''

    if not (isinstance(term, int) and term >= 0):
        raise ValueError("'term' has to be bigger than 0 and 'int'.")

    _result = _.fibonacci(term)
    result = _result.value
    _.free(_result)

    return result


if __name__ == "__main__":
    pass
