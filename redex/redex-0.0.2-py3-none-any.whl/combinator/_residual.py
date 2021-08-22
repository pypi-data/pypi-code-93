"""The residual combinator."""

from redex import operator as op
from redex import util
from redex.function import Fn, FnIter
from redex import function as fn
from redex.combinator._serial import serial, Serial
from redex.combinator._branch import branch


def residual(*children: FnIter, shortcut: Fn = op.identity) -> Serial:
    """Creates a residual combinator.

    The combinator computes the sum of two branches: main and shortcut.

    >>> import operator as op
    >>> from redex import combinator as cb
    >>> residual = cb.residual(cb.serial(op.add, op.add))
    >>> residual(1, 2, 3) == 1 + 2 + 3 + 1
    True

    Args:
        children: a main sequence of functions.
        shortcut: a skip connection. Defaults to identity function.

    Returns:
        a combinator.
    """
    flat_children = util.flatten(children)
    if len(flat_children) == 1:
        grouped_children = flat_children[0]
    else:
        grouped_children = serial(*flat_children)

    grouped_children_signature = fn.infer_signature(grouped_children)
    if grouped_children_signature.n_out != 1:
        raise ValueError(
            "The main branch of the residual must output exactly one value. "
            f"`{fn.infer_name(grouped_children)}` outputs "
            f"`{grouped_children_signature.n_out}` values."
        )
    shortcut_signature = fn.infer_signature(shortcut)
    if shortcut_signature.n_out != 1:
        raise ValueError(
            "The shortcut branch of the residual must output exactly one value. "
            f"`{fn.infer_name(shortcut)}` outputs `{shortcut_signature.n_out}` values."
        )

    return serial(
        branch(grouped_children, shortcut),
        op.add,
    )
