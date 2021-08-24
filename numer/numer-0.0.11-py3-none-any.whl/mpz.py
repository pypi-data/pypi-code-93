import ctypes as c
import os

_ = c.CDLL(os.path.abspath('gmp.so'))

_.pfib.argtypes = (c.c_ulonglong,)

_.factorial.argtypes = (c.c_ulong,)
_.factorial.restype = c.c_char_p

def print_fib(term_count: int):
    '''prints fibonacci series up to term_count'''

    if not (isinstance(term_count, int) and term_count > 0):
        raise ValueError("'term_count' has to be bigger than 0 and 'int'.")

    _.pfib(term_count)

def factorial(term: int) -> int:
    '''prints the factorial of `term`.'''

    if not (isinstance(term, int) and term >= 0):
        raise ValueError("'term' has to be bigger than 0 and 'int'.")

    return int(_.factorial(term).decode('utf-8'))


if __name__ == "__main__":
    pass
