"""The select combinator."""

from typing import Optional, List
from redex.function import Signature
from redex.stack import stackmethod, Stack
from redex.combinator._base import Combinator

# pylint: disable=too-few-public-methods
class Select(Combinator):
    """The select combinator."""

    indices: List[int]
    """a sequence of 0-based indices relative to the top of the stack."""

    @stackmethod
    def __call__(self, stack: Stack) -> Stack:
        selected = tuple(stack[i] for i in self.indices)
        return selected + stack[self.signature.n_in :]


def select(indices: List[int], n_in: Optional[int] = None) -> Select:
    """Creates a select combinator.

    The combinator allows to change order or copy inputs.

    >>> from redex import combinator as cb
    >>> select = cb.select([0, 0, 1, 1])
    >>> select(1, 2, 3, 4) == (1, 1, 2, 2, 3, 4)
    True

    Args:
        indices: a sequence of 0-based indices relative to the top of the stack.
        n_in: a number of items to pop from the stack, and replace with
            those specified by `indices`. If not specified, the value will be
            calculated as `max(indices) + 1`.

    Returns:
        a combinator.
    """
    n_out = len(indices)
    if n_in is None:
        n_in = max(indices) + 1 if len(indices) != 0 else 0

    return Select(signature=Signature(n_in=n_in, n_out=n_out), indices=indices)
