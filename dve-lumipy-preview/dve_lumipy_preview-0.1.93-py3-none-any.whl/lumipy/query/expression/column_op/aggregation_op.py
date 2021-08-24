from lumipy.query.expression.column_op.base_aggregation_op import BaseAggregateColumn
from lumipy.query.expression.sql_value_type import numerics, SqlValType
from lumipy.query.expression.column.column_base import BaseColumnExpression


class Count(BaseAggregateColumn):
    """Class representing a count column aggregate

    """

    def __init__(self, column: BaseColumnExpression):
        """__init__ method for count class

        Args:
            column: column expression to apply count expression to.
        """
        super().__init__(
            column,
            'count',
            lambda x: f"count({x.get_sql()})",
            lambda x: True,
            lambda x: SqlValType.Int
        )


class Average(BaseAggregateColumn):
    """Class representing a mean column aggregate

    """

    def __init__(self, column: BaseColumnExpression):
        """__init__ method for average class

        Args:
            column: column expression to apply average expression to.
        """
        super().__init__(
            column,
            'avg',
            lambda x: f"avg({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Double
        )


class Sum(BaseAggregateColumn):
    """Class representing a sum column aggregate

    """

    def __init__(self, column: BaseColumnExpression):
        """__init__ method for sum class

        Args:
            column: column expression to apply sum expression to.
        """
        super().__init__(
            column,
            'total',
            lambda x: f"total({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: x
        )


class Min(BaseAggregateColumn):
    """Class representing a min column aggregate

    """

    def __init__(self, column: BaseColumnExpression):
        """__init__ method for min class

        Args:
            column: column expression to apply min expression to.
        """
        super().__init__(
            column,
            'min',
            lambda x: f"min({x.get_sql()})",
            lambda x: True,
            lambda x: x
        )


class Max(BaseAggregateColumn):
    """Class representing a max column aggregate

    """

    def __init__(self, column: BaseColumnExpression):
        """__init__ method for max class

        Args:
            column: column expression to apply max expression to.
        """
        super().__init__(
            column,
            'max',
            lambda x: f"max({x.get_sql()})",
            lambda x: True,
            lambda x: x
        )


class Median(BaseAggregateColumn):
    """Class representing a median column aggregate

    """

    def __init__(self, column: BaseColumnExpression):
        """__init__ method for median class

        Args:
            column: column expression to apply median expression to.
        """
        super().__init__(
            column,
            'median',
            lambda x: f"median({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: x
        )


class Stdev(BaseAggregateColumn):
    """Class representing a stdev column aggregate

    """

    def __init__(self, column: BaseColumnExpression):
        """__init__ method for stdev class

        Args:
            column: column expression to apply stdev expression to.
        """
        super().__init__(
            column,
            'stdev',
            lambda x: f"stdev({x.get_sql()})",
            lambda x: x in numerics,
            lambda x: SqlValType.Double
        )


class Quantile(BaseAggregateColumn):
    """Class representing a quantile calculation over a column

    """

    def __init__(self, column: BaseColumnExpression, quantile: float):
        """__init__ method of the quantile class

        Args:
            column (BaseColumnExpression): column to apply quantile expression to
            quantile (float): the value of the quantile. Must be between 0 and 1.
        """
        from lumipy.query.expression.column.column_literal import python_to_expression
        quantile_lit = python_to_expression(quantile)
        super().__init__(
            column,
            'quantile',
            lambda x, y: f"quantile({x.get_sql()}, {y.get_sql()})",
            lambda x, y: x in numerics and y == SqlValType.Double,
            lambda x, y: x,
            quantile_lit
        )
