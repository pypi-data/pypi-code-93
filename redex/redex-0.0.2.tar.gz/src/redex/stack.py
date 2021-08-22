"""The stack is used by combinators to pass data between functions."""

from typing import Any, Callable, Optional
from functools import wraps
import logging
from redex import util
from redex import function as fn
from redex.function import Fn, Signature

# TODO: enable type check after: mypy > 0.910.
# https://github.com/python/mypy/issues/9980
Stack = tuple[Any, ...]  # type:ignore
"""The stack."""

StackMethod = Callable[[Any, Stack], Stack]
"""The method from stack state to stack state."""


def constrained_call(
    func: Fn,
    stack: Stack,
    signature: Optional[Signature] = None,
) -> Stack:
    """Applies the function with arguments taken from the stack.

    Takes `n_in` arguments from the stack, reshapes them to match
    function's input shape `in_shape`, calls the function, then
    pushes ouputs back onto the stack.

    Args:
        func: a function to call.
        stack: arguments available for the call.
        signature: optional signature of the function. If not set,
            it will be inferred.

    Returns:
        function outputs and rest of the stack.

    Raises:
        ValueError: if a number of arguments on the stack less
            than required for function call.

    >>> import operator as op
    >>> from redex.stack import constrained_call
    >>> constrained_call(func=op.add, stack=(1, 2, 0, 0))
    (3, 0, 0)
    """
    if signature is None:
        signature = fn.infer_signature(func)

    n_in, in_shape = signature.n_in, signature.in_shape
    stack_size = len(stack)

    logging.debug(
        "constrained_call :: %s stack_size=%s  signature=%s",
        fn.infer_name(func).ljust(20),
        stack_size,
        signature,
    )

    verify_stack_size(func, stack, signature)
    inputs = util.reshape_tuples(stack[:n_in], in_shape)
    outputs = tuple(util.flatten_tuples(util.expand_to_tuple(func(*inputs))))
    return outputs + stack[n_in:]


def verify_stack_size(
    func: Fn,
    stack: Stack,
    signature: Optional[Signature] = None,
) -> int:
    """Verifies that the stack contains required number of arguments for function call.

    Args:
        func: a function.
        stack: arguments available for the call.
        signature: optional signature of the function. If not set,
            it will be inferred.

    Returns:
        stack size.

    Raises:
        ValueError: if a number of arguments on the stack less
            than required for function call.
    """
    if signature is None:
        signature = fn.infer_signature(func)

    n_in = signature.n_in
    stack_size = len(stack)
    if stack_size < n_in:
        raise ValueError(
            f"The `{fn.infer_name(func)}` takes {n_in} "
            f"positional arguments but {stack_size} were given."
        )
    return stack_size


def stackmethod(method: Fn) -> StackMethod:
    """Wraps a any method to a stackmethod.

    The stackmethods expect an entire stack as a single argument
    and output its modified version.

    Args:
        method: a method to wrap.

    Returns:
        a stackmethod.

    ::

        from redex.stack import stackmethod, Stack
        class Add:
            @stackmethod
            def __call__(self, stack: Stack) -> Stack:
                a, b, *rest = stack
                return (a + b, *rest)
        Add()(1, 2)  # -> 3
    """

    @wraps(method)
    def inner(self: Any, *inputs: Any) -> Any:
        return util.squeeze_tuple(method(self, util.expand_to_tuple(inputs)))

    return inner
