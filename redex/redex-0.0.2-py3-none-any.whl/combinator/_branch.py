"""The branch combinator."""

from typing import List
from functools import reduce
from redex import util
from redex import function as fn
from redex.function import Fn, FnIter
from redex.combinator._serial import serial, Serial
from redex.combinator._parallel import parallel
from redex.combinator._select import select


def branch(*children: FnIter) -> Serial:
    """Creates a branch combinator.

    The combinator combines multiple branches of given functions
    and operate on copy of inputs. Each branch includes a sequence
    of functions applied serially.

    >>> import operator as op
    >>> from redex import combinator as cb
    >>> branch = cb.branch(cb.serial(op.add, op.add), op.add)
    >>> branch(1, 2, 3) == (1 + 2 + 3, 1 + 2)
    True

    Args:
        children: a sequence of functions.

    Returns:
        a combinator.
    """
    flat_children = util.flatten(children)
    indices = _estimate_branch_indices(flat_children)
    return serial(
        select(indices=indices),
        parallel(*flat_children),
    )


def _estimate_branch_indices(children: List[Fn]) -> List[int]:
    def count(acc: List[int], child: Fn) -> List[int]:
        signature = fn.infer_signature(child)
        return acc + list(range(0, signature.n_in))

    initializer: List[int] = []
    return reduce(count, children, initializer)
