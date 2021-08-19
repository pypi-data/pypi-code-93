"""Python to HTML.

Example
-------
>>> from htmlclasses import E, to_string
>>> class html(E):
...     class body(E):
...         class p(E):
...             TEXT = 'foo'
...         class p(E):
...             TEXT = 'bar'
...             some_attr = 'note the hyphen in the actual HTML'
...         class p(E):
...             TEXT = 'baz'
...             class_ = 'note trailing underscore'
...
>>> print(to_string(html, indent='    '))
<!DOCTYPE html>
<html>
    <body>
        <p>foo</p>
        <p some-attr="note the hyphen in the actual HTML">bar</p>
        <p class="note trailing underscore">baz</p>
    </body>
</html>
"""

from .htmlclasses import E  # noqa: F401
from .serialize import to_string  # noqa: F401

__all__ = ('E', 'to_string')

__version__ = '0.3.1'
