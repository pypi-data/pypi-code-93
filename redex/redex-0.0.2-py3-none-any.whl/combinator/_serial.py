"""The serial combinator."""

from typing import List
from functools import reduce
from redex.combinator._base import Combinator
from redex import util
from redex import function as fn
from redex.function import Fn, FnIter, Signature
from redex.stack import constrained_call, stackmethod, Stack


# pylint: disable=too-few-public-methods
class Serial(Combinator):
    """The serial combinator."""

    children: List[Fn]
    """composite functions."""
    children_signatures: List[Signature]
    """signatures of the composite functions."""

    @stackmethod
    def __call__(self, stack: Stack) -> Stack:
        for i, child in enumerate(self.children):
            signature = self.children_signatures[i]
            stack = constrained_call(child, stack, signature)
        return stack


def serial(*children: FnIter) -> Serial:
    """Creates a serial combinator.

    The combinator applies functions in series (function composition).

    >>> import operator as op
    >>> from redex import combinator as cb
    >>> serial = cb.serial(op.add, op.add, op.add)
    >>> serial(1, 2, 3, 4) == 1 + 2 + 3 + 4
    True

    Args:
        children: a sequence of functions.

    Returns:
        a combinator.
    """
    flat_children = util.flatten(children)
    signature, children_signatures = _estimate_sequential_signatures(flat_children)
    return Serial(
        signature=signature,
        children=flat_children,
        children_signatures=children_signatures,
    )


_Initializer = tuple[int, int, List[Signature]]


def _estimate_sequential_signatures(
    children: List[Fn],
) -> tuple[Signature, List[Signature]]:
    def count(acc: _Initializer, child: Fn) -> _Initializer:
        in_max, in_total, signatures = acc
        signature = fn.infer_signature(child)
        in_total += signature.n_in
        return (
            max(in_max, in_total),
            in_total - signature.n_out,
            signatures + [signature],
        )

    initializer: _Initializer = (0, 0, [])
    in_max, in_total, children_signatures = reduce(count, children, initializer)
    return Signature(n_in=in_max, n_out=in_max - in_total), children_signatures
