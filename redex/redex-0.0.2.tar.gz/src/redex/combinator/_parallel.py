"""The parallel combinator."""

from typing import List
from functools import reduce
from dataclasses import replace
from redex import util
from redex import function as fn
from redex.function import Fn, FnIter, Signature
from redex.stack import constrained_call, stackmethod, Stack
from redex.combinator._base import Combinator

# pylint: disable=too-few-public-methods


# pylint: disable=too-few-public-methods
class Parallel(Combinator):
    """The parallel combinator."""

    children: List[Fn]
    """composite functions."""

    children_signatures: List[Signature]
    """signatures of the composite functions."""

    @stackmethod
    def __call__(self, stack: Stack) -> Stack:
        outputs = Stack()
        for i, child in enumerate(self.children):
            signature = self.children_signatures[i]
            n_lower, n_upper = signature.index_bounds
            outputs += constrained_call(child, stack[n_lower:n_upper], signature)
        return outputs + stack[self.signature.n_in :]


def parallel(*children: FnIter) -> Parallel:
    """Creates a parallel combinator.

    The combinator applies functions in parallel to its inputs. Each function
    consumes a span of inputs. The span sizes are determined by a number of
    required arguments of these functions.

    >>> import operator as op
    >>> from redex import combinator as cb
    >>> parallel = cb.parallel(op.add, op.add)
    >>> parallel(1, 2, 3, 4) == (1 + 2, 3 + 4)
    True

    Args:
        children: a sequence of functions.

    Returns:
        a combinator.
    """
    flat_children = util.flatten(children)
    signature, children_signatures = _estimate_parallel_signatures(flat_children)
    return Parallel(
        signature=signature,
        children=flat_children,
        children_signatures=children_signatures,
    )


_Initializer = tuple[int, int, List[Signature]]


def _estimate_parallel_signatures(
    children: List[Fn],
) -> tuple[Signature, List[Signature]]:
    def count(acc: _Initializer, child: Fn) -> _Initializer:
        in_total, out_total, signatures = acc
        signature = replace(fn.infer_signature(child), start_index=in_total)
        return (
            in_total + signature.n_in,
            out_total + signature.n_out,
            signatures + [signature],
        )

    initializer: _Initializer = (0, 0, [])
    in_total, out_total, children_signatures = reduce(count, children, initializer)
    return Signature(n_in=in_total, n_out=out_total), children_signatures
