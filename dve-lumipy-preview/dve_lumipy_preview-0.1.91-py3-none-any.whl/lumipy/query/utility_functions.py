from .expression.column.column_ordering import AscendingOrder, DescendingOrder
from .expression.column.column_literal import LiteralColumn
from .expression.column.column_alias import AliasedColumn
from typing import Union

"""
Utility functions for constructing queries that augment the fluent syntax. 
"""


def ordering_index(index: int, ascending: bool = True) -> Union[AscendingOrder, DescendingOrder]:
    """Make an ordering expression from a column index number.

    Args:
        index (int): the index value.
        ascending (bool): whether it's ascending order (True) or descending (False).

    Returns:
        Union[AscendingOrder, DescendingOrder]: Ordering expression for a numeric index.
    """
    if ascending:
        return AscendingOrder(index)
    else:
        return DescendingOrder(index)


def literal_with_alias(literal, alias: str) -> AliasedColumn:
    """Make an alias applied to a string literal.

    Args:
        literal (str): the string literal.
        alias (str): the alias to apply.

    Returns:
        AliasedColumn: the aliased literal column expression.
    """
    return LiteralColumn(literal).with_alias(alias)
