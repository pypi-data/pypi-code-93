"""Operator is just a function."""

from operator import add, sub
from redex.operator._identity import identity

__all__ = [
    "add",
    "sub",
    "identity",
]
