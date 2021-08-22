"""Functions are building blocks for algorithms."""

import types
import inspect
from typing import Any, Callable, Iterable, List, NoReturn, Optional, Union
from dataclasses import dataclass
from functools import reduce
from redex import util


@dataclass
class Signature:
    """The function signature.

    The signature describes properties essential for a function
    to work on the stack. These properties either inferred from function
    type annotation or set explicitly.
    """

    n_in: int
    """the number of inputs expected by the function."""

    n_out: int
    """the number of outputs of the function."""

    start_index: int = 0
    """the index on a stack for the first input."""

    in_shape: tuple[Any, ...] = ()
    """the shape of inputs with `()` meaning the function doesn't
    have any input arguments."""

    def __post_init__(self) -> None:
        """Initializes the shape of inputs if its value isn't
        set explicitly."""
        if not self.in_shape and self.n_in != 0:
            self.in_shape = _infer_flat_input_shape(n_args=self.n_in)

    @property
    def index_bounds(self) -> tuple[int, int]:
        """index bounds on the stack for inputs."""
        start = self.start_index
        return (start, start + self.n_in)


@dataclass
class FineCallable:
    """The callable object with a signature."""

    signature: Signature
    """a signature of the function."""


Fn = Callable[..., Any]
"""The function."""

FnIter = Union[Fn, Iterable[Fn]]
"""A single function or sequence of functions."""
# FnIter = Union[Fn, Iterable["FnIter"]]
# NOTE: recursive types are not supported by mypy.
# https://github.com/python/mypy/issues/731


def infer_name(func: Fn) -> str:
    """Infers a name of the function.

    Args:
        func: a function.

    Returns:
        a name of the function or callable object.
    """
    if isinstance(
        func,
        (
            types.FunctionType,
            types.MethodType,
            types.BuiltinFunctionType,
            types.BuiltinMethodType,
        ),
    ):
        return func.__name__
    return type(func).__name__


def infer_signature(func: Fn) -> Signature:
    """Infers a signature of the function.

    Args:
        func: a function.

    Returns:
        the function signature.

    Raises:
        ValueError: if the annotation include variadic tuples.
            Variadic tuples nested in other then tuple annotations
            (e.g. `Sequence(tuple[Any, ...])`) are fine.
    """
    if isinstance(func, FineCallable):
        return func.signature

    signature = inspect.signature(func)
    try:
        n_out = _count_outputs(func, signature)
        in_shape = _infer_input_shape(func, signature)
    except ValueError as err:
        raise ValueError(
            f"Connot infer a signature of the function `{infer_name(func)}`, "
            "because its type annotation include variadic tuple annotation "
            "such as `tuple[Any,...]` or `tuple`."
        ) from err

    n_in = len(util.flatten_tuple_annotation_shape(in_shape)) if in_shape else 0
    return Signature(
        n_in=n_in,
        n_out=n_out,
        in_shape=in_shape,
    )


def _count_outputs(func: Fn, signature: Optional[inspect.Signature] = None) -> int:
    """Counts a number of outputs of the function.

    A number of outputs are inferred from the return type annotation.
    - If return annotation isn't available, a single output is assumed.
    - Multiple outputs must be defined as a parameterized tuple.
    - Functions may not return any value. `None` is an acceptible return value.

    Args:
        func: a function.
        signature: optional signature of the function. If not set,
            it will be inferred.

    Raises:
        ValueError: if the annotation include variadic tuples.
            Variadic tuples nested in other then tuple annotations
            (e.g. `Sequence(tuple[Any, ...])`) are fine.
    """
    if signature is None:
        signature = inspect.signature(func)

    output_type = signature.return_annotation
    if output_type is inspect.Signature.empty:
        # The number of outputs of the function cannot be estimated,
        # becase its return annotation is missing. Our best guess `n_out=1`.
        # TODO: should we log a warning?
        return 1

    if isinstance(output_type, types.GenericAlias) and output_type.__origin__ is tuple:
        # `ValueError` may be reised if type annotation include variadic tuples.
        shape = util.infer_tuple_annotation_shape(output_type)
        return len(util.flatten_tuple_annotation_shape(shape))

    if output_type is None:
        return 0

    if output_type is NoReturn:
        raise ValueError(
            "Operation must return outputs eventually. "
            f"The function `{infer_name(func)}` doesn't return any value, "
            "becase outputs are defined with `NoReturn` type."
        )

    # An output of any type but `tuple` is a single value.
    return 1


def _infer_input_shape(
    func: Fn,
    signature: Optional[inspect.Signature] = None,
) -> tuple[Any, ...]:
    """Infers a shape of required function arguments.

    A shape of inputs are inferred from annotations of function arguments:
    - Any argument without default value is counted as a single input.
    - Each parameter of a tuple is counted as an independent input.
    - Arguments of the `None` type are ignored.

    Args:
        func: a function.
        signature: optional signature of the function. If not set,
            it will be inferred.

    Returns:
        a shape of required (e.g. without default value) function arguments.

    Raises:
        ValueError: if the annotation include variadic tuples.
            Variadic tuples nested in other then tuple annotations
            (e.g. `Sequence(tuple[Any, ...])`) are fine.
    """

    def add_required_arg_shape(acc: List[Any], arg: Any) -> List[Any]:
        if arg.default != inspect.Parameter.empty:
            return acc

        if arg.annotation is None:
            return acc

        # `ValueError` may be reised if type annotation include variadic tuples.
        shape = util.infer_tuple_annotation_shape(arg.annotation)
        return acc + [shape]

    if signature is None:
        signature = inspect.signature(func)

    shapes: List[Any] = reduce(
        add_required_arg_shape, signature.parameters.values(), []
    )
    return tuple(shapes)


def _infer_flat_input_shape(n_args: int) -> tuple[Any, ...]:
    """Compute a shape of inputs that function are not tuples.

    Args:
        n_args: a number of inputs.

    Returns:
        a shape of inputs.
    """
    return tuple([()] * n_args)
