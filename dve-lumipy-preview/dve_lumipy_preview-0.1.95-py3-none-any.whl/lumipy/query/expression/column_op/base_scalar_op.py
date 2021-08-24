from abc import abstractmethod

from ..column.column_base import BaseColumnExpression
from ..column.column_literal import python_to_expression, LiteralColumn
from lumipy.query.expression.column.column_alias import AliasedColumn
from lumipy.query.expression.column.source_column import SourceColumn
from ..column.column_prefix import PrefixedColumn
from .base_aggregation_op import BaseAggregateColumn
from typing import Callable
from functools import reduce


class BaseScalarOp(BaseColumnExpression):
    """Base class for expressions that represent scalar operations on columns: i.e. functions that map a column of
    values to another column of values.

    """

    @abstractmethod
    def __init__(
            self,
            op_name: str,
            sql_op_fn: Callable,
            type_check_fn: Callable,
            return_type_fn: Callable,
            *values: BaseColumnExpression
    ):
        """__init__ method of the BaseScalarOp class.

        Args:
            op_name (str): name of the scalar column op.
            sql_op_fn (Callable): function that takes SQL string pieces and makes the SQL piece for this op
            type_check_fn (Callable): function that checks the sql value types of the parents.
            return_type_fn (Callable): function that determines the output sql value type of this expression.
            *values (BaseColumnExpression): input values to the scalar column op expression. Must be a column expression
            (inheritor of BaseColumnExpression)
        """

        # Handle python primitive inputs: convert them to LiteralColumn instances.
        in_values = [python_to_expression(v) for v in values]
        # noinspection PyTypeChecker
        # Unwrap aliases.
        in_values = [v.get_original() if isinstance(v, AliasedColumn) else v for v in in_values]

        # Get source table hashes so this expression can be distingished from one from another table but with
        # identical column names.
        table_sources = []
        for v in in_values:
            v_type = type(v)
            if v_type == SourceColumn or v_type == PrefixedColumn or v_type == LiteralColumn:
                # noinspection PyArgumentList
                table_sources.append(v.source_table_hash())
            elif issubclass(v_type, BaseScalarOp) or issubclass(v_type, BaseAggregateColumn):
                # noinspection PyArgumentList
                for col in v.get_col_dependencies():
                    table_sources.append(col.source_table_hash())

        table_hash = reduce(lambda x, y: x ^ y, set(table_sources))

        super().__init__(
            table_hash,
            sql_op_fn,
            type_check_fn,
            return_type_fn,
            op_name,
            *in_values
        )
