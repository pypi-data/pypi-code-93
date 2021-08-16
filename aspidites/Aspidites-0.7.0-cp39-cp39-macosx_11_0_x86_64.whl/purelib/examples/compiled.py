# cython: language_level=3, annotation_typing=True, c_string_encoding=utf-8
# THIS FILE IS GENERATED - DO NOT EDIT #
import cython  # type: ignore
from typing import Any
from collections.abc import Generator
from pyrsistent import (
    pset, 
    pmap, 
    pvector, 
    s, v, m, 
    PRecord,
    PClass
)
from Aspidites.woma import *
from Aspidites._vendor import F, _
from Aspidites.monads import Maybe, Surely, Undefined, SafeDiv, SafeMod, SafeExp
from Aspidites._vendor.contracts import contract, new_contract
from Aspidites._vendor.RestrictedPython import safe_builtins
# DECLARATIONS TO ALLOW CONTRACTS TO TYPE CHECK #
procedure: None
coroutine: Generator
number: Any
globals().update(dict(__builtins__=safe_builtins))  # add all imports to globals


# comment_line 1:`first-class functions`
@contract()
@cython.binding(True)
def Add(x : 'int' = 3, y : 'int' = 3) -> 'int':
    return x+y


# comment_line 6:`generators`
@contract()
def Yield123() -> 'coroutine':
    yield Maybe(Add, 0, 1)()
    yield Maybe(Add, 0, 2)()
    yield Maybe(Add, 0, 3)()


# comment_line 12:`procedures`
@contract()
def Hello() -> 'procedure':
    return Maybe(print, "Hello, World!")()


# comment_line 16:`coroutines`
@contract()
def Hello2() -> 'coroutine':
    yield Maybe(Hello, )()


# comment_line 20:`persistent vectors`
D = pvector([2, 4, 6, 8, 10])
# comment_line 23:`persistent sets`
G = pset({'a', 'b', 'c'})
# comment_line 26:`persistent mappings`
C = pmap({'a': (3+5), 'b': 8, 'c': True, 4: None, 'd': Maybe(SafeExp, 6, 2*5+3)})
# comment_line 33:`new contracts can impose more complex contractual clauses`
new_contract('colors', 'list[3](int,<256)')
# comment_line 36:`any woma function can be closed in place to become an instance that complies with the`
# comment_line 37:`type specification or Undefined for instances that breach the type specification contract`
x = Maybe(Add, 3, 3)
# comment_line 40:`seamless exception handling allows tracing of undefined code branches`
y = Maybe(Add, 4, 3.5)
# comment_line 43:`mixed usage of closure and regular function calls`
z = Maybe(Add, Maybe(x, )(), 3)()
# comment_line 46:`Scala-style closure functions`
scala = (_*2)
val = Maybe(scala, _+_)()
val = Maybe(val, scala)
# comment_line 51:`modulus and division by 0 handled by returning Undefined()`
denom = 0
div_by_zero = Maybe(SafeDiv, 1, denom)
mod_zero = Maybe(SafeMod, 1, denom)
div_by_zero2 = Maybe(SafeDiv, 1, 0)
mod_zero2 = Maybe(SafeMod, 1, 0)
# comment_line 58:`main: structure for executable actions when run as a binary`
if __name__ == "__main__":
    Maybe(Hello, )()
    Maybe(print, "I'm a binary.")()

