"""General utility functions."""

import types
from typing import Any, Callable, Iterable, List
from functools import reduce

PredicateFn = Callable[[Any], bool]
SelectFn = Callable[[Any], Iterable[Any]]


def expand_to_tuple(item: Any) -> tuple[Any, ...]:
    """Wraps anything but tuple into a tuple.

    Args:
        item: any sequence or a single item.

    Returns:
        a tuple.

    >>> from redex import util
    >>> util.expand_to_tuple((1,))
    (1,)
    >>> util.expand_to_tuple((1,2))
    (1, 2)
    """
    return item if isinstance(item, tuple) else (item,)


def squeeze_tuple(item: Any) -> Any:
    """Reduces a tuple to a single item if only it consists of
    a single item.

    Args:
        item: any sequence or a single item.

    Returns:
        a single item if possible, or an input sequence if not.

    >>> from redex import util
    >>> util.squeeze_tuple((1,))
    1
    >>> util.squeeze_tuple((1,2))
    (1, 2)
    """
    return item[0] if isinstance(item, tuple) and len(item) == 1 else item


def flatten(item: Any) -> List[Any]:
    """Recursively flatten any sequence but a string or bytes.

    Args:
        item: a sequence or a single item. A single item will be packet into a list.

    Returns:
        a list with tuples got flattened.

    >>> from redex import util
    >>> util.flatten([1, [(2, 3), 4]])
    [1, 2, 3, 4]
    >>> util.flatten(1)
    [1]
    """
    return _flatten(
        item,
        predicate=_is_iterable_butnot_stringlike,
        select=_identity,
    )


def flatten_tuples(item: Any) -> List[Any]:
    """Recursively flatten tuples in a sequence.

    Args:
        item: a sequence or a single item. A single item will be packet into a list.

    Returns:
        a list with tuples got flattened.

    >>> from redex import util
    >>> util.flatten_tuples((1, ((2, 3), 4)))
    [1, 2, 3, 4]
    >>> util.flatten_tuples(1)
    [1]
    """
    return _flatten(
        item,
        predicate=_is_tuple,
        select=_identity,
    )


def flatten_tuple_annotations(annotation: Any) -> List[Any]:
    """Recursively flatten tuples in the type annotation.

    Args:
        annotation: a type annotation.

    Returns:
        a list with tuple annotations got flattened.

    Raises:
        ValueError: if the annotation include variadic tuples.
            Variadic tuples nested in other then tuple annotations
            (e.g. `Sequence(tuple[Any, ...])`) are fine.

    >>> from redex import util
    >>> from typing import Any
    >>> util.flatten_tuple_annotations(tuple[Any, tuple[tuple[Any, Any], Any]])
    [typing.Any, typing.Any, typing.Any, typing.Any]
    >>> util.flatten_tuple_annotations(Any)
    [typing.Any]
    """
    return _flatten(
        annotation,
        predicate=_is_parameterized_tuple_anotation,
        select=_generic_arguments,
    )


def flatten_tuple_annotation_shape(shape: tuple[Any, ...]) -> List[Any]:
    """Recursively flatten tuple annotation shapes.

    Flattening a single shaped item `((),)` and a single flat item `()`
    both result into a single item list `[()]`.

    Args:
        shape: annotation shape.

    Returns:
        a flat list of annotation shapes.

    >>> from redex import util
    >>> util.flatten_tuple_annotation_shape(((), (((), ()), ())))
    [(), (), (), ()]
    >>> util.flatten_tuple_annotation_shape(((),))
    [()]
    >>> util.flatten_tuple_annotation_shape(())
    [()]
    """
    return _flatten(
        shape,
        predicate=bool,
        select=_identity,
    )


def infer_tuple_annotation_shape(annotation: Any) -> tuple[Any, ...]:
    """Recursively infer shapes of the tuples in the type annotation.

    Each tuple in the annotation shape represent an item.

    Note that:
    - `((), ((), ()))` represents some shape, for example `tuple[Any, tuple[Any, Any]]`.
    - `((),)` represents a single shaped item, meaning `tuple[Any]`.
    - `()` represents an unshaped item, such as `Any` or `int`.
    - `None` is acceptable value.


    Args:
        annotation: a type annotation.

    Returns:
        annotation shapes.

    Raises:
        ValueError: if the annotation include variadic tuples.
            Variadic tuples nested in other then tuple annotations
            (e.g. `Sequence(tuple[Any, ...])`) are fine.

    >>> from redex import util
    >>> from typing import Any
    >>> util.infer_tuple_annotation_shape(tuple[Any, tuple[tuple[Any, Any], Any]])
    ((), (((), ()), ()))
    >>> util.infer_tuple_annotation_shape(tuple[Any])
    ((),)
    >>> util.infer_tuple_annotation_shape(Any)
    ()
    >>> util.infer_tuple_annotation_shape(None)
    ()
    """

    def inner(acc: tuple[Any, ...], annotation: Any) -> tuple[Any, ...]:
        if _is_parameterized_tuple_anotation(annotation):
            initializer: tuple[Any, ...] = ()
            return (*acc, reduce(inner, _generic_arguments(annotation), initializer))
        return (*acc, ())

    if _is_parameterized_tuple_anotation(annotation):
        initializer: tuple[Any, ...] = ()
        return reduce(inner, _generic_arguments(annotation), initializer)

    return ()


def reshape_tuples(item: Any, shape: tuple[Any, ...]) -> Any:
    """Recursively shape a sequence into tuples.

    Args:
        item: a flat sequence or a single item.
        shape: a desired shape.

    Returns:
        shaped tuples or original input for the shape `()`.

    Raises:
        RuntimeError: if input sequence wasn't entirely consumed.
            It can only happen if there is a difference in the number
            of items in the input sequence and provided shape.

    >>> from redex import util
    >>> util.reshape_tuples((1,2,3,4), ((),(((),()),())))
    (1, ((2, 3), 4))
    >>> util.reshape_tuples(1, ())
    1
    """

    def inner(
        acc: tuple[Any, tuple[Any, ...]],
        shape: Any,
    ) -> tuple[Any, tuple[Any, ...]]:
        flat, shaped = acc
        if shape and _is_iterable_butnot_stringlike(flat):
            initializer: tuple[Any, tuple[Any, ...]] = (flat, ())
            flat_rest, shaped_subitems = reduce(inner, shape, initializer)
            return (
                flat_rest,
                (*shaped, shaped_subitems),
            )
        return (
            flat[1:],
            (*shaped, flat[0]),
        )

    if not shape:
        return item

    if not _is_iterable_butnot_stringlike(item):
        return (item,)

    initializer: tuple[Any, tuple[Any, ...]] = (item, ())
    _flat, shaped = reduce(inner, shape, initializer)
    if _flat:
        raise RuntimeError(
            f"Failed to reshape tuples `{item}` into shape `{shape}`. ",
            f"Input sequence must be entirely consumed, but some part of it left `{_flat}`",
        )

    return shaped


def _flatten(
    item: Any,
    predicate: PredicateFn,
    select: SelectFn,
) -> List[Any]:
    """Recursively flatten a sequence.

    Args:
        item: a sequence or a single item. A single item will be packet into a list.
        predicate: for each item of the sequence, the function determines
            whether the item should be flattened.
        select: selects nested items to proceed.

    Returns:
        a list with items determined by `predicate` got flattened.
    """

    def inner(acc: List[Any], item: Any) -> List[Any]:
        if predicate(item):
            return acc + reduce(inner, select(item), [])
        return acc + [item]

    if predicate(item):
        return reduce(inner, select(item), [])

    return [item]


def _identity(item: Iterable[Any]) -> Iterable[Any]:
    """Always returns the same value that was used as its argument."""
    return item


def _generic_arguments(annotation: types.GenericAlias) -> tuple[Any, ...]:
    """Returns arguments of the parameterized tuple.

    Args:
        annotation: a parameterized tuple annotation.

    Returns:
        tuple arguments.
    """
    return annotation.__args__


def _is_iterable_butnot_stringlike(item: Any) -> bool:
    """Verifies if item instance is an iterator,
    but not of a string or bytes type.

    Args:
        item: an item to verify.

    Returns:
        `True` if verified, `False` otherwise.
    """
    return isinstance(item, Iterable) and not isinstance(item, (bytes, str))


def _is_tuple(item: Any) -> bool:
    """Verifies if item instance is a tuple.

    Args:
        item: an item to verify.

    Returns:
        `True` if verified, `False` otherwise.
    """
    return isinstance(item, tuple)


def _is_parameterized_tuple_anotation(annotation: Any) -> bool:
    """Verifies if type annotation is a parameterized tuple.

    Args:
        item: a type annotation.

    Returns:
        `True` if verified, `False` otherwise.

    Raises:
        ValueError: if the annotation include variadic tuples.
            Variadic tuples nested in other then tuple annotations
            (e.g. `Sequence(tuple[Any, ...])`) are fine.
    """
    if annotation in (tuple, Ellipsis):
        raise ValueError(
            "Connot flatten a variadic tuple annotation "
            "such as `tuple[Any,...]` or `tuple`."
        )
    return isinstance(annotation, types.GenericAlias) and annotation.__origin__ is tuple
