"""Boto3 predicate-driven retrieval of AWS resources.

Boto3 utility library that supports parameter-driven and
predicate-driven retrieval of collections of AWS
resources.
"""

from __future__ import annotations
import doctest

def get(method, arguments=None, constraints=None, attribute=None):
    """
    Assemble all items in a paged response pattern from
    the supplied AWS API retrieval method.

    >>> import itertools
    >>> def method(identifier, position=None):
    ...     if position is None:
    ...         position = 0
    ...     return dict({
    ...         'items': [{'value': position, 'parity': position % 2}],
    ...     }, **({'position': position + 1} if position <= 4 else {}))
    >>> [item['value'] for item in itertools.islice(get(
    ...     method,
    ...     arguments={'identifier': 0},
    ...     constraints={'parity': 0}
    ... ), 0, 4)]
    [0, 2, 4]
    """
    arguments = {} if arguments is None else arguments
    constraints = {} if constraints is None else constraints
    attribute = 'items' if attribute is None else attribute
    position = {}
    while True:
        response = method(**arguments, **position)
        for item in response.get(attribute, []):
            if all(item[k] == v for (k, v) in constraints.items()):
                yield item
        if not 'position' in response:
            break
        position = {'position': response['position']}

if __name__ == "__main__":
    doctest.testmod() # pragma: no cover
