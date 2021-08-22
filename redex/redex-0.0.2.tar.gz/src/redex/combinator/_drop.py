"""The drop combinator."""

from redex.function import Signature
from redex.stack import stackmethod, verify_stack_size, Stack
from redex.combinator._base import Combinator

# pylint: disable=too-few-public-methods
class Drop(Combinator):
    """The drop combinator."""

    @stackmethod
    def __call__(self, stack: Stack) -> Stack:
        verify_stack_size(self, stack, self.signature)
        n_in = self.signature.n_in
        return stack[n_in:]


def drop(n_in: int = 1) -> Drop:
    """Creates a duplicate combinator.

    Drops some of inputs.

    >>> from redex import combinator as cb
    >>> drop = cb.drop()
    >>> drop(1, 2) == 2
    True

    Args:
        n_in: a number of inputs.

    Returns:
        a combinator.
    """
    return Drop(signature=Signature(n_in=n_in, n_out=0))
