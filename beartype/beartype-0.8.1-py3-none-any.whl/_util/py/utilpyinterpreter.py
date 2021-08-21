#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python interpreter** utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.cache.utilcachecall import callable_cached
from platform import python_implementation

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ TESTERS                           }....................
@callable_cached
def is_py_pypy() -> bool:
    '''
    ``True`` only if the active Python interpreter is **PyPy**.

    This tester is memoized for efficiency.
    '''

    return python_implementation() == 'PyPy'
