'''
Psypher - A modern asymmetric encryption scheme.

Basic Usage:
```py
>>> from psypher import Scheme
>>> s1, s2 = Scheme.default(), Scheme.default()
```
Key export and import:
```py
>>> s1.receive(s2.export()) # binary
>>> s2.receiveJson(s1.exportJson()) # JSON
```
Signature:
```py
>>> s = s1.sign(b'data')
>>> s2.verify(b'data', s)
True
>>> s2.verify(b'attack', s)
False
```
Encryption:
```py
>>> e = s1.encrypt(b'data')
>>> s2.decrypt(e)
b'data'
```
'''

class Error(Exception):
    'General base class for all errors in psypher.'

from .scheme import Scheme

__all__ = ['Scheme', 'Error']