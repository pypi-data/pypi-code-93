""" Various utilities that don't fit into any particular module. """

import enum
from collections import defaultdict
from functools import reduce, wraps
from inspect import iscoroutinefunction, ismethod
from itertools import chain
from typing import Any, Callable, Iterable, Iterator, List, Mapping, Type, Union


def coroutine(fn: Callable) -> Callable:
    """Decorator to convert a regular function to a coroutine function.

    Since asyncio.coroutine is set to be removed in 3.10, this allows
    awaiting a regular function. Not useful as a @-based decorator,
    but very helpful for inline conversions of unknown functions, and
    especially lambdas.
    """
    if iscoroutinecallable(fn):
        return fn

    @wraps(fn)
    async def _wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return _wrapper


def iscoroutinecallable(obj: Callable):
    """Return `True` if the object is a coroutine callable.

    Similar to `inspect.iscoroutinefunction`, except that it also accepts
    objects with coroutine `__call__` methods.
    """
    return iscoroutinefunction(obj) or (
        callable(obj)
        and ismethod(obj.__call__)  # type: ignore
        and iscoroutinefunction(obj.__call__)  # type: ignore
    )


def get_all_subclasses(cls: Type) -> List[Type]:
    """Returns a dict containing all the subclasses of the given class.

    Follows the inheritance tree recursively.
    """
    subclasses = list(cls.__subclasses__())
    if subclasses:
        subclasses.extend(chain.from_iterable(get_all_subclasses(c) for c in subclasses))
    return subclasses


def fnmap(functions: Iterable[Callable[[Any], Any]], *values: Any) -> Union[Any, Iterator[Any]]:
    """Applies a series of single-argument functions to each of the values.

    Returns a single value if one value was given, or an iterator if multiple.
    """
    results = map(lambda val: reduce(lambda v, fn: fn(v), functions, val), values)
    return next(results) if len(values) == 1 else results


def get_fnmap(*functions: Callable[[Any], Any]) -> Callable[..., Any]:
    """ Prepares a single-argument function to apply all the functions. """
    return lambda *values: fnmap(functions, *values)


class CollectionEnum(enum.EnumMeta):
    """Metaclass which allows lookup on enum values.

    The default implementation of `EnumMeta.__contains__` looks
    for instances of the Enum class, which is not very useful.
    With this, it is possible to check whether an Enum class
    contains a certain value.

    Usage:
        >>> class MyEnum(enum.Enum, metaclass=CollectionEnum):
        ...     FOO = "foo"
        ...     BAR = "bar"
        ...
        >>> "foo" in MyEnum
        True
        >>> "blah" in MyEnum
        False
        >>> MyEnum.BAR in MyEnum
        True
    """

    def __contains__(cls, item):
        return isinstance(item, cls) or item in [v.value for v in cls.__members__.values()]


def flatten_mapping(values: Iterable) -> Iterable:
    """Extract an iterable of values from an iterable of nested mappings.

    Usage:
        >>> values = ({"a": {"b": "c"}, "d": {"e": "f"}}, {"g": "h"})
        >>> tuple(flatten_mapping(values))
        ('c', 'f', 'h')
    """
    for item in values:
        if isinstance(item, Mapping):
            yield from flatten_mapping(item.values())
        else:
            yield item


def nested_dict():
    """Creates a recursive defaultdict of any depth.

    Usage:
        >>> d = nested_dict()
        >>> d["a"] = 1
        >>> d["b"]["c"] = 2
        >>> d == {"a": 1, "b": {"c": 2}}
        True
    """
    return defaultdict(nested_dict)
