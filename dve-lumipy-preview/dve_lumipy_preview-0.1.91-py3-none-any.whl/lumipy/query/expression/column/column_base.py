from abc import abstractmethod
from typing import Callable, Union

from lumipy.navigation.field_metadata import FieldMetadata
from lumipy.query.expression.base_sql_expression import BaseSqlExpression
from lumipy.query.expression.sql_value_type import SqlValType
import datetime as dt


class BaseColumnExpression(BaseSqlExpression):
    """Base class for all of the column classes. Contains the overloads that allow constructon of
    column expressions out of base column class inheritors and python operators.

    Each inheritor of BaseColumnExpression should represent a SQL operation on a column. They are combined together to
    form a directed acyclic graph of expressions that describes the operations that are combined to make a SQL query.
    """

    @abstractmethod
    def __init__(
            self,
            source_table_hash: int,
            sql_str_fn: Callable,
            type_check_fn: Callable,
            data_type_fn: Callable,
            op_name: str,
            *values: Union['BaseColumnExpression', FieldMetadata]
    ):
        """__init__ method for the base column expression class.

        Args:
            source_table_hash (int): hash of the source table this column originated from.
            sql_str_fn (Callable): function that turns the parent values into a SQL piece string.
            type_check_fn (Callable): function that checks the sql value types of the parents.
            return_type_fn (Callable): function that determines the output sql value type of this expression.
            op_name (Callable): name of the operation this class represents.
            *values Union[BaseColumnExpression, FieldDescription]: parent values of the expression.
        """

        self._source_table_hash = source_table_hash

        super().__init__(
            op_name,
            sql_str_fn,
            type_check_fn,
            data_type_fn,
            *values
        )

    def source_table_hash(self) -> int:
        """Get the __hash__ value of the column's source table.

        Returns:
            int: the source table hash value.
        """
        return self._source_table_hash

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def sum(self) -> 'Sum':
        """Apply a sum expression (sql = 'total()') to the column expression.

        This resolves to a 'total' op rather than 'sum' op so the that the behaviour when summing a column of nulls
        matches the pandas dataframe behaviour (sum of a column of nulls is equal to zero).

        This will only work for expressions that resolve to numeric SQL value types.

        Returns:
            Sum: sum aggregate expression object of this column expression.
        """
        from lumipy.query.expression.column_op.aggregation_op import Sum
        return Sum(self)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def count(self) -> 'Count':
        """Apply a count expression (sql = 'count([col])') to the column expression.

        The 'count' op will count the number of elements in a column.

        Returns:
            Count: count aggregate expression object of this column expression.
        """
        from lumipy.query.expression.column_op.aggregation_op import Count
        return Count(self)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def avg(self) -> 'Average':
        """Apply an avg (equivalent to a mean, sql = 'avg([col])') expression to the column expression

        This will only work for expressions that resolve to numeric SQL value types.

        Returns:
            Average: avg aggregate expression object of this column expression.
        """
        from lumipy.query.expression.column_op.aggregation_op import Average
        return Average(self)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def mean(self) -> 'Average':
        """Equivalent to the avg method. Applies an expression that represents computing the mean of a column.

        This will only work for expressions that resolve to numeric SQL value types.

        Returns:
            Average: avg aggregate expression object of this column expression.

        """
        return self.avg()

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def min(self) -> 'Min':
        """Apply a min expression to this column expression (sql = 'min([col])').

        This will only work for expressions that resolve to numeric SQL value types.

        Returns:
            Min: min expression object applied to this column expression.
        """
        from lumipy.query.expression.column_op.aggregation_op import Min
        return Min(self)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def max(self) -> 'Max':
        """Apply a max expression to this column expression (sql = 'max([col])').

        This will only work for expressions that resolve to numeric SQL value types.

        Returns:
            Max: max expression object applied to this column expression.
        """
        from lumipy.query.expression.column_op.aggregation_op import Max
        return Max(self)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def median(self) -> 'Median':
        """Apply a median aggregate expression to this column expression (sql = 'median([col])').

        This will only work for expressions that resolve to numeric SQL value types.

        The 'median' op computes the median value of the input. The median is the 'middle value' that separates the top
        half of an ordered set of values from the lower half.
        This input can be a column or an expression made out of columns: e.g. stdev(col1*col2).

        Returns:
            Median: median expression object applied to this column expression.
        """
        from lumipy.query.expression.column_op.aggregation_op import Median
        return Median(self)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def stdev(self) -> 'Stdev':
        """Apply a standard deviation aggregate expression to this column expression (sql = 'stdev([col])')

        The 'stdev' op computes the standard deviation of the input. This input can be a column or an expression made
        out of columns: e.g. stdev(col1*col2).

        This will only work for expressions that resolve to numeric SQL value types.

        Returns:
            Stdev: stdev expression object applied to this column expression.
        """
        from lumipy.query.expression.column_op.aggregation_op import Stdev
        return Stdev(self)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def quantile(self, value: float) -> 'Quantile':
        """Apply a quantile aggregate expression to this column expression (sql = 'quantile([col], value)')

        Computes the value of a given quantile of the input (the value that bounds this fraction of the data). For
        example a quantile of 0.9 will be the value that 90% of the data is below.

        Args:
            value: the value of the quantile to evaluate.

        Returns:
            Quantile: quantile expression object applied to this oclumn expression.
        """
        if value < 0 or value > 1:
            raise ValueError("Quantiles are only defined between 0 and 1.")

        from lumipy.query.expression.column_op.aggregation_op import Quantile
        return Quantile(self, value)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def ascending(self) -> 'AscendingOrder':
        """Apply an ascending order expression to the column expression (sql = '[col] asc').

        Returns:
            AscendingOrder: ascending order expression built from this column expression.
        """
        from .column_ordering import AscendingOrder
        return AscendingOrder(self)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def descending(self) -> 'DescendingOrder':
        """Apply a descending order expression to the column expression (sql = '[col] asc').

        Returns:
            DescendingOrder: descending order expression built from this column expression.
        """
        from .column_ordering import DescendingOrder
        return DescendingOrder(self)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def with_alias(self, alias: str) -> 'AliasedColumn':
        """Apply an alias expression to the column expression (sql = '[col] as my_alias')

        Args:
            alias (str): alias to apply to the column

        Returns:
            AliasedColumn: aliased column expression build from the column expression.

        """
        from lumipy.query.expression.column.column_alias import AliasedColumn
        return AliasedColumn(self, alias)

    def __hash__(self):
        return hash(self.source_table_hash() + super().__hash__())

    def __add__(self, other):
        from ..column_op.binary_op import Add
        return Add(self, other)

    def __sub__(self, other):
        from ..column_op.binary_op import Sub
        from .column_literal import python_to_expression
        other_val = python_to_expression(other)
        if other_val.get_type() == SqlValType.DateTime:
            return self.unixepoch() - other_val.unixepoch()
        else:
            return Sub(self, other)

    def __rsub__(self, other):
        from ..column_op.binary_op import Sub
        from .column_literal import python_to_expression
        other_val = python_to_expression(other)
        if other_val.get_type() == SqlValType.DateTime:
            return other_val.unixepoch() - self.unixepoch()
        else:
            return Sub(other, self)

    def __mul__(self, other):
        from ..column_op.binary_op import Mul
        return Mul(self, other)

    def __mod__(self, other):
        from ..column_op.binary_op import Mod
        return Mod(self, other)

    def __floordiv__(self, other):
        from ..column_op.binary_op import Div
        return Div(self, other)

    def __truediv__(self, other):
        from ..column_op.binary_op import Div
        from .column_literal import python_to_expression
        other_val = python_to_expression(other)
        return Div(self, other_val.cast(float))

    def __radd__(self, other):
        from ..column_op.binary_op import Add
        return Add(other, self)

    def __rmul__(self, other):
        from ..column_op.binary_op import Mul
        return Mul(other, self)

    def __rmod__(self, other):
        from ..column_op.binary_op import Mod
        return Mod(other, self)

    def __rtruediv__(self, other):
        from ..column_op.binary_op import Div
        return Div(other, self.cast(float))

    def __rfloordiv__(self, other):
        from ..column_op.binary_op import Div
        return Div(other, self)

    def __and__(self, other):
        from ..column_op.binary_op import And
        return And(self, other)

    def __or__(self, other):
        from ..column_op.binary_op import Or
        return Or(self, other)

    def __xor__(self, other):
        from ..column_op.binary_op import BitwiseXor
        return BitwiseXor(self, other)

    def __invert__(self):
        from ..column_op.unary_op import Not
        return Not(self)

    def __eq__(self, other):
        from ..column_op.binary_op import Equals
        return Equals(self, other)

    def __ne__(self, other):
        from ..column_op.binary_op import NotEquals
        return NotEquals(self, other)

    def __gt__(self, other):
        from ..column_op.binary_op import GreaterThan
        return GreaterThan(self, other)

    def __lt__(self, other):
        from ..column_op.binary_op import LessThan
        return LessThan(self, other)

    def __ge__(self, other):
        from ..column_op.binary_op import GreaterThanOrEqual
        return GreaterThanOrEqual(self, other)

    def __neg__(self):
        from ..column_op.unary_op import Negative
        return Negative(self)

    def __le__(self, other):
        from ..column_op.binary_op import LessThanOrEqual
        return LessThanOrEqual(self, other)

    def __rand__(self, other):
        from ..column_op.binary_op import And
        return And(other, self)

    def __ror__(self, other):
        from ..column_op.binary_op import Or
        return Or(other, self)

    def __rxor__(self, other):
        from ..column_op.binary_op import BitwiseXor
        return BitwiseXor(other, self)

    def __pow__(self, power, modulo=None):
        from ..column_op.binary_op import Power
        return Power(self, power)

    def __rpow__(self, other):
        from ..column_op.binary_op import Power
        return Power(other, self)

    def __ceil__(self):
        from ..column_op.unary_op import Ceil
        return Ceil(self)

    def __floor__(self):
        from ..column_op.unary_op import Floor
        return Floor(self)

    def __abs__(self):
        from ..column_op.unary_op import Abs
        return Abs(self)

    def __round__(self, n=None):
        from ..column_op.binary_op import Round
        if n is not None and n < 0:
            raise ValueError("Number of places to round a value to must be non-negative!")
        return Round(self, n if n is not None else 0)

    def cast(self, val_type: type) -> 'CastTo':
        """Apply a CAST operation to this expression. This will cast a column of one type to another.

        For example, to cast an integer column to text do
            table.int_col.cast(str)

        Args:
            val_type (type): a python type corresponding to target type. Valid options are int, bool, str, float

        Returns:
            CastTo: a CastTo expression object representing the cast op.
        """

        from ..column_op.binary_op import CastTo

        if val_type == int:
            return CastTo(self, SqlValType.Int.name)
        elif val_type == bool:
            return CastTo(self, SqlValType.Boolean.name)
        elif val_type == str:
            return CastTo(self, SqlValType.Text.name)
        elif val_type == float:
            return CastTo(self, SqlValType.Double.name)
        else:
            valid_types = [int, bool, str, float]
            raise TypeError(
                f"Invalid input to cast: {val_type}. "
                f"Supported inputs are the types {', '.join(t.__name__ for t in valid_types)}."
            )

    def exp(self) -> 'Exp':
        """Apply an exponential expression to this column expression.

        Returns:
            Exp: Exp instance representing this operation.
        """
        from ..column_op.unary_op import Exp
        return Exp(self)

    def log(self):
        """Apply a natural logarithm expression to this column expression.

        Returns:
            LogE: LogE instance representing this operation.
        """
        from ..column_op.unary_op import LogE
        return LogE(self)

    def log10(self):
        """Apply a base 10 logarithm expression to this column expression.

        Returns:
            Log10: Log10 instance representing this operation.
        """
        from ..column_op.unary_op import Log10
        return Log10(self)

    def str_len(self):
        """Apply a string length (len) expression to this column expression.

        Returns:
            Len: Len instance representing this operation.
        """
        from ..column_op.unary_op import Len
        return Len(self)

    def sqrt(self):
        """Apply a sqrt expression to this column expression.

        Returns:
            Power: Power instance representing this operation.
        """
        return self**0.5

    def square(self):
        """Apply a square power expression to this column expression.

        Returns:
            Power: Power instance representing this operation.
        """
        return self**2

    def ceil(self):
        """Apply a ceil expression to this column expression.

        This rounds a double up to the next integer.
        You can also apply python's math.ceil function to a column expression to get the same effect.

        Returns:
            Ceil: Ceil instance representing this operation.
        """
        return self.__ceil__()

    def floor(self):
        """Apply a floor expression to this column expression.

        This rounds a double down to the next integer.
        You can also apply python's math.floor function to a column expression to get the same effect.

        Returns:
            Floor: Floor instance representing this operation.
        """
        return self.__floor__()

    def abs(self):
        """Apply an abs value expression to this column expression.

        Gives the absolute value of a numeric value, so abs(-2) = 2.
        You can also use python's built-in abs() function in place of this method.

        Returns:
            Abs: Abs instance representing this expression.
        """
        return self.__abs__()

    def round(self, n_places=None):
        """Apply a rounding expression to this column expression.

        Will give the value of the input expression rounded to some number of places (default to 0 - nearest int).
        You can also use python's build-in round() function in place of this method.

        Args:
            n_places (int): number of places to round to

        Returns:
            Round: Round instance representing this expression.
        """
        return self.__round__(n_places)

    def sign(self):
        """Apply a sign expression to this column expression

        This will give -1, 0 or 1 depending on the numeric value the input expression resolves to
        (negative / zero / positive).

        Returns:
            Sign: Sign instance representing this expression.
        """
        from ..column_op.unary_op import Sign
        return Sign(self)

    def trim(self, trim_str=None, trim_type='both'):
        """Apply a trim expression to this column expression.

        This will trim characters from the left, right or both (default = both) ends of a string.
        If no target value to trim is given the operation will trim any whitespace instead.

        Args:
            trim_str (Optional[str]): substring to trim from the string expression.
            trim_type (str): string denoting which trim type to use ('left', 'right', or 'both')

        Returns:
            Trim: Trim instance representing this expression.
        """
        from ..column_op.binary_op import Trim

        trim_text = trim_str if trim_str is not None else ''

        if trim_type.lower() == 'both':
            return Trim(self, trim_text, '')
        elif trim_type.lower() == 'left':
            return Trim(self, trim_text, 'l')
        elif trim_type.lower() == 'right':
            return Trim(self, trim_text, 'r')
        else:
            raise ValueError(
                f"Invalid trim type '{trim_type}'. Must be one of 'right', 'left' or 'both'. Defaults to 'both'."
            )

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def like(self, other: str) -> 'Like':
        """Apply a 'like' condition expression to this expression (sql = '[col] like '%example%')

        The like operation is for case-insensitive pattern matching in strings where you're looking for a value located
        somewhere in the string. There are two wildcards: '%' which matches and sequence of characters and '_' which
        matches any single character.

        This expression and the argument to like must both resolve to Text SQL value types.

        Args:
            other (Union[str, BaseColumnExpression]): string literal or a column expression that resolves to Text SQL
            value type.

        Returns:
            Like: the Like expression object that represents this operation.
        """
        from ..column_op.binary_op import Like
        return Like(self, other)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def not_like(self, other: str) -> 'NotLike':
        """Apply a 'not like' condition expression to this expression (sql = '[col] not like '%example%').

        The not like operation is the negation of case-insensitive pattern matching in strings where you're looking for
        a value located somewhere in the string. There are two wildcards: '%' which matches and sequence of characters
        and '_' which matches any single character.

        This expression and the argument to not like must both resolve to Text SQL value types.

        Args:
            other (Union[str, BaseColumnExpression]): string literal or a column expression that resolves to Text SQL
            value type.

        Returns:
            NotLike: the NotLike expression object that represents this operation.

        """
        from ..column_op.binary_op import NotLike
        return NotLike(self, other)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def glob(self, other: str) -> 'Glob':
        """Apply a 'glob' condition expression to this expression (sql = '[col] glob '*example*').

        The glob operation does unix-style string pattern matching. It is case sensitive and there are two wildcards:
        '*' will match any sequence of characters '?' matches a single character.

        This expression and the argument to glob must both resolve to Text SQL value types.

        Args:
            other (Union[str, BaseColumnExpression]): string literal or a column expression that resolves to Text SQL
            value type.

        Returns:
            Glob: the Glob expression object that represents this operation.

        """
        from ..column_op.binary_op import Glob
        return Glob(self, other)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def not_glob(self, other: str) -> 'NotGlob':
        """Apply a 'not glob' condition expression to this expression (sql = '[col] not glob '*example*').

        Negation of the glob operation that does unix-style string pattern matching. It is case sensitive and there are
        two wildcards '*' will match any sequence of characters '?' matches a single character.

        This expression and the argument to not glob must both resolve to Text SQL value types.

        Args:
            other (Union[str, BaseColumnExpression]): string literal or a column expression that resolves to Text SQL
            value type.

        Returns:
            NotGlob: the NotGlob expression object that represents this operation.

        """
        from ..column_op.binary_op import NotGlob
        return NotGlob(self, other)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def regexp(self, other) -> 'Regexp':
        """Apply a 'regexp' condition expression to this expression (sql = '[col] regexp 'example[0-9A-Za-z]*$').

        The regexp operation checks whether a regular expression finds a match in the input string. It is case sensitive.

        This expression and the argument to regexp must both resolve to Text SQL value types.

        Args:
            other (Union[str, BaseColumnExpression]): string literal or a column expression that resolves to Text SQL
            value type.

        Returns:
            Regexp : the Regexp expression object that represents this operation.

        """
        from ..column_op.binary_op import Regexp
        return Regexp(self, other)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def not_regexp(self, other) -> 'NotRegexp':
        """Apply a 'not regexp' condition expression to this expression (sql = '[col] not regexp 'example[0-9A-Za-z]*$').

        Negation of the regexp operation that checks whether a regular expression finds a match in the input string. It is case sensitive.

        This expression and the argument to not regexp must both resolve to Text SQL value types.

        Args:
            other (Union[str, BaseColumnExpression]): string literal or a column expression that resolves to Text SQL
            value type.

        Returns:
            NotRegexp : the NotRegexp expression object that represents this operation.

        """
        from ..column_op.binary_op import NotRegexp
        return NotRegexp(self, other)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def is_null(self) -> 'IsNull':
        """Apply an 'is null' condition expresson to this expression (sql = '[col] is null').

        Conditional operation that evaluates whether a value is null.

        Returns:
            IsNull: the IsNull instance that represents 'is null' applied to this expression.
        """
        from ..column_op.unary_op import IsNull
        return IsNull(self)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def is_not_null(self) -> 'NotIsNull':
        """Apply an 'is not null' condition expresson to this expression (sql = '[col] is not null').

        Conditional operation that evaluates whether a value is not null.

        Returns:
            NotIsNull: the NotIsNull instance that represents 'is not null' applied to this expression.
        """
        from ..column_op.unary_op import IsNotNull
        return IsNotNull(self)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def is_in(self, *others) -> 'IsIn':
        """Apply 'in' expression to this expression given a list of values (sql = '[col] in ('A', 'B', 'C')'.

        The 'in' op is a conditional that evaluates whether a column value is a member of an array.

        Args:
            others:

        Returns:
            IsIn: the IsIn instance that represents the 'in' condition applied to this expression and argument.
        """
        from ..column_op.binary_op import IsIn
        from lumipy.query.expression.column.collection import CollectionExpression
        from collections.abc import Sequence

        if len(others) == 0:
            raise ValueError("Empty arg for IN.")
        elif len(others) == 1 and isinstance(others[0], Sequence):
            collection = CollectionExpression(*others[0])
            return IsIn(self, collection)
        else:
            collection = CollectionExpression(*others)
            return IsIn(self, collection)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def not_in(self, *others) -> 'NotIn':
        """Apply 'not in' expression to this expression given a list of values (sql = '[col] not in ('A', 'B', 'C')'.

        The 'not in' op is a conditional that evaluates whether a column value is not a member of an array.

        Args:
            other List[Union[str, int, float]]: list of python primitives to check non-membership of.

        Returns:
            NotIn: the NotIn instance that represents the 'not in' op applied to this expression and argument.
        """
        from ..column_op.binary_op import NotIn
        from lumipy.query.expression.column.collection import CollectionExpression
        from collections.abc import Sequence

        if len(others) == 0:
            raise ValueError("Empty arg for NOT IN.")
        elif len(others) == 1 and isinstance(others[0], Sequence):
            collection = CollectionExpression(*others[0])
            return NotIn(self, collection)
        else:
            collection = CollectionExpression(*others)
            return NotIn(self, collection)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def between(self, other1, other2) -> 'Between':
        """Apply 'between' expression to this expression given two values that define an interval
        (sql = '[col] between 1 and 2').

        The 'between' op is a conditional that evaluates whether a column value is between two values.
        The SQL value types of this expression and the arguments must resolve to either numerics, date or datetime; or
        be int, float, date, datetime python objects.

        Args:
            other1 Union[int, float, datetime, BaseColumnExpression]: lower limit of the interval.
            other2 Union[int, float, datetime, BaseColumnExpression]: upper limit of the interval.

        Returns:
            Between: the Between instance that represents the 'between' op applied to this expression.
        """
        from ..column_op.ternary_op import Between
        return Between(self, other1, other2)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def not_between(self, other1, other2) -> 'NotBetween':
        """Apply 'not between' expression to this expression given two values that define an interval
        (sql = '[col] not between 1 and 2').

        The 'not between' op is a conditional that evaluates whether a column value is not between two values.
        The SQL value types of this expression and the arguments must resolve to either numerics, date or datetime; or
        be int, float, date, datetime python objects.

        Args:
            other1 Union[int, float, datetime, BaseColumnExpression]: lower limit of the interval.
            other2 Union[int, float, datetime, BaseColumnExpression]: upper limit of the interval.

        Returns:
            NotBetween: the NotBetween instance that represents the 'not between' op applied to this expression.
        """
        from ..column_op.ternary_op import NotBetween
        return NotBetween(self, other1, other2)

    # noinspection PyUnresolvedReferences
    # import for use in type check will cause circ ref
    def concat(self, other: Union[str, 'BaseColumnExpression'], where: str = 'end') -> 'StringConcat':
        """Concatenate this column expression with another (sql = 'x | y'). Only valid for expressions
        that resolve to Text SQL value type.

        Args:
            other (Union[str, BaseSqlExpression]): other expression that resolves to a column of SQL Text values.
            where (str): where to concatente the str: "start" or "end" (defaults to "end").
        Returns:
            StringConcat: expression that represents the string concat of this column and other.
        """
        from ..column_op.binary_op import StringConcat
        if where.lower() == 'end':
            return StringConcat(self, other)
        elif where.lower() == 'start':
            return StringConcat(other, self)
        else:
            raise ValueError(f"Invalid input for the where arg: {where}. Must be 'start' or 'end'.")

    def replace(self, target: Union[str, 'BaseColumnExpression'], substitute: Union[str, 'BaseColumnExpression']):
        """Apply a replace expression to this column expression.

        Will swap all occurrences of the substring with the supplied replacement value.

        Args:
            target (Union[str, BaseColumnExpression]): target value to replace - can a string literal or column expression.
            substitute (Union[str, BaseColumnExpression]): value to replace with - can be string literal or column expression.

        Returns:
            StrReplace: StrReplace instance representing the replace expression applied to this column expression.
        """
        from ..column_op.ternary_op import StrReplace
        return StrReplace(self, target, substitute)

    def lower(self):
        """Apply a lower expression to this column expression.

        Lower will convert a text value to all lower case.

        Returns:
            LowerCase: LowerCase instance representing the lower expression applied to this column expression.
        """
        from ..column_op.unary_op import LowerCase
        return LowerCase(self)

    def upper(self):
        """Apply an upper expression to this column expression.

        Upper will convert a text value to all upper case.

        Returns:
            UpperCase: UpperCase instance representing the lower expression applied to this column expression.
        """
        from ..column_op.unary_op import UpperCase
        return UpperCase(self)

    def soundex(self):
        """Apply a soundex expression to this column expression.

        Soundex returns an English phonetic representation of a given text value.

        Returns:
            Soundex: Soundex instance representing the soundex expression applied to this column expression.
        """
        from ..column_op.unary_op import Soundex
        return Soundex(self)

    def substr(self, start_ind: Union[int, 'BaseColumnExpression'], length: Union[int, 'BaseColumnExpression'] = 1):
        """Apply a substr expression to this column expression.

        Gets a substring of a given length starting at a given index starting at 1. Index and length can be negative,
        this denotes indexing/length from the end of the string.

        Args:
            start_ind (Union[int, 'BaseColumnExpression']): starting index of the substring.
            length (Union[int, 'BaseColumnExpression']): length of the substring (default = 1).

        Returns:
            Substr: Substr instance representing a substr expression to this column expression.
        """
        if isinstance(start_ind, int) and start_ind == 0:
            raise ValueError(
                f'Invalid input for start_ind: 0. '
                f'SQL substring index must be a positive non-zero int (indexing from string start) or negative '
                f'(indexing backward from string end).'
            )

        from ..column_op.ternary_op import Substr
        return Substr(self, start_ind, length)

    def unicode(self):
        """Apply a unicode expression to this column expression.

        Unicode SQL function returns the unicode int value for the first character in a string.

        Returns:
            Unicode: Unicode instance representing a unicode expression applied to this column expression.
        """
        from ..column_op.unary_op import Unicode
        return Unicode(self)

    def replicate(self, times: Union[int, 'BaseColumnExpression']):
        """Apply a replicate expression to this column expression.

        Replicate will return a string value repeated a give number of times. For example replicate('ABC', 3) will give
        'ABCABCABC.

        Args:
            times Union[int, BaseColumnExpression]: number of times to repeat the string.

        Returns:
            Replicate: Replicate instance the represents the expression applied to this column expression.
        """
        from ..column_op.binary_op import Replicate
        return Replicate(self, times)

    def reverse(self):
        """Apply a reverse expression to this column expression.

        Reverse will return the string with the characters in reverse order.

        Returns:
            Reverse: Reverse instance representing the reverse expression applied to this column expression.
        """
        from ..column_op.unary_op import Reverse
        return Reverse(self)

    def left_str(self, n_char: Union[int, 'BaseColumnExpression']):
        """Apply a leftstr expression to this column expression.

        Leftstr will get the substring consisting of the first n-many character from the left.

        Args:
            n_char (Union[int, BaseColumnExpression]): number of characters to take from the left.

        Returns:
            LeftStr: LeftStr instance representing a leftstr expression applied to this column expression.
        """
        from ..column_op.binary_op import LeftStr
        if isinstance(n_char, int) and n_char < 1:
            raise ValueError("n_char must be positive and non-zero.")
        return LeftStr(self, n_char)

    def right_str(self, n_char: Union[int, 'BaseColumnExpression']):
        """Apply a rightstr expression to this column expression.

        Leftstr will get the substring consisting of the first n-many character from the right.

        Args:
            n_char (Union[int, BaseColumnExpression]): number of characters to take from the right.

        Returns:
            RightStr: RightStr instance representing a rightstr expression applied to this column expression.
        """
        from ..column_op.binary_op import RightStr
        if isinstance(n_char, int) and n_char < 1:
            raise ValueError("n_char must be positive and non-zero.")
        return RightStr(self, n_char)

    def pad_str(self, length: Union[int, 'BaseColumnExpression'], pad_type: Union[str, 'BaseColumnExpression']):
        """Apply a pad expression to this column expression.

        Pads out a string with whitespace so it reaches a given length.

        Args:
            length (Union[int, BaseColumnExpression]): target length of padded string.
            pad_type (Union[str, BaseColumnExpression]): type of pad operation: 'right', 'left' or 'center'.

        Returns:
            Pad: Pad instance representing the expression applied to this column expression.
        """
        from ..column_op.binary_op import Pad
        if pad_type.lower() == 'right':
            return Pad(self, length, 'r')
        elif pad_type.lower() == 'left':
            return Pad(self, length, 'l')
        elif pad_type.lower() == 'center':
            return Pad(self, length, 'c')
        else:
            raise ValueError(f'Unrecognised pad type: {pad_type}')

    def str_filter(self, filter_str: Union[str, 'BaseColumnExpression']):
        """Apply a strfilter expression to this column expression.

        Strfilter will filter a string for the characters that exist in another string.

        Args:
            filter_str (Union[str, BaseColumnExpression]): string value or text valued expression containing the
            characters to filter for.

        Returns:
            Strfilter: Strfilter instance representing the expression applied to this column expression.
        """
        from ..column_op.binary_op import StrFilter
        return StrFilter(self, filter_str)

    def index(self, chars: str, start_position: int = 0):
        """Apply an index (charindex) expression to this column expression.

        Index (charindex) will find the index of the first occurrence of a substring after a specified starting position.

        Args:
            chars Union[str, BaseColumnExpression]: substring to locate.
            start_position Union[str, BaseColumnExpression]: starting position of the search (defaults to 0)

        Returns:
            Index: Index instance representing the expression applied to this column expression.
        """
        from lumipy.query.expression.column_op.ternary_op import Index
        return Index(chars, self, start_position)

    def proper(self):
        """Apply a proper expression to this column expression.

        Proper will capitalize each word in a string delimited by spaces so
            'arthur morgan'
        becomes
            'Arthur Morgan'

        Returns:
            Proper: Proper instance representing the expression applied to this column expression.
        """
        from ..column_op.unary_op import Proper
        return Proper(self)

    def contains(self, sub_str: Union[str, 'BaseColumnExpression'], case_sensitive: bool = False):
        """Test whether a string-valued column expression contains a given substring.

        Args:
            sub_str (Union[str, BaseColumnExpression]): string value or column expression that resolves to a substring
            to check for
            case_sensitive (bool): whether to do a case-sensitive (Glob) or case-insensitive (Like) search.

        Returns:
            Union[Glob, Like]: Glob or Like instance representing the expression applied to this column.
        """
        if not isinstance(case_sensitive, bool):
            raise TypeError(f"The case_sensitive arg to contains method must be a bool. "
                            f"Was {type(case_sensitive).__name__}")

        if case_sensitive and isinstance(sub_str, str):
            return self.glob(f"*{sub_str}*")
        elif case_sensitive and issubclass(type(sub_str), BaseColumnExpression):
            arg_expr = sub_str.concat('*').concat('*', where='start')
            return self.glob(arg_expr)
        elif not case_sensitive and isinstance(sub_str, str):
            return self.like(f"%{sub_str}%")
        elif not case_sensitive and issubclass(type(sub_str), BaseColumnExpression):
            arg_expr = sub_str.concat('%').concat('%', where='start')
            return self.like(arg_expr)
        else:
            raise TypeError(f"sub_str type must be str or a column expression. Was {type(sub_str).__name__}.")

    def startswith(self, sub_str: Union[str, 'BaseColumnExpression'], case_sensitive: bool = False):
        """Test whether a string-valued column expression starts with a given substring.

        Args:
            sub_str (Union[str, BaseColumnExpression]): string value or column expression that resolves to a substring
            to check for
            case_sensitive (bool): whether to do a case-sensitive (Glob) or case-insensitive (Like) search.

        Returns:
            Union[Glob, Like]: Glob or Like instance representing the expression applied to this column.
        """
        if case_sensitive and isinstance(sub_str, str):
            return self.glob(f"{sub_str}*")
        elif case_sensitive and issubclass(type(sub_str), BaseColumnExpression):
            arg_expr = sub_str.concat('*')
            return self.glob(arg_expr)
        elif not case_sensitive and isinstance(sub_str, str):
            return self.like(f"{sub_str}%")
        elif not case_sensitive and issubclass(type(sub_str), BaseColumnExpression):
            arg_expr = sub_str.concat('%')
            return self.like(arg_expr)
        else:
            raise TypeError(f"sub_str type must be str or a column expression. Was {type(sub_str).__name__}.")

    def endswith(self, sub_str: Union[str, 'BaseColumnExpression'], case_sensitive: bool = False):
        """Test whether a string-valued column expression ends with a given substring.

        Args:
            sub_str (Union[str, BaseColumnExpression]): string value or column expression that resolves to a substring
            to check for
            case_sensitive (bool): whether to do a case-sensitive (Glob) or case-insensitive (Like) search.

        Returns:
            Union[Glob, Like]: Glob or Like instance representing the expression applied to this column.
        """
        if case_sensitive and isinstance(sub_str, str):
            return self.glob(f"*{sub_str}")
        elif case_sensitive and issubclass(type(sub_str), BaseColumnExpression):
            arg_expr = sub_str.concat('*', where='start')
            return self.glob(arg_expr)
        elif not case_sensitive and isinstance(sub_str, str):
            return self.like(f"%{sub_str}")
        elif not case_sensitive and issubclass(type(sub_str), BaseColumnExpression):
            arg_expr = sub_str.concat('%', where='start')
            return self.like(arg_expr)
        else:
            raise TypeError(f"sub_str type must be str or a column expression. Was {type(sub_str).__name__}.")

    def coalesce(self, *values: Union[str, float, int, bool, dt.datetime, 'BaseColumnExpression']):
        """Apply a coalesce expression to this column expression.

        Coalesce will take a series of values and assign the first non-null value as its output.

        Args:
            *values (Union[str, float, int, bool, dt.datetime, 'BaseColumnExpression']): values to supply to the
            coalesce expression. Can be python literals or column expressions.

        Returns:
            Coalesce: Coalesce instance representing the expression applied to this column expression.
        """
        from lumipy.query.expression.column_op.variadic_op import Coalesce
        return Coalesce(self, *values)

    def strftime(self, dt_format: Union[str, 'BaseColumnExpression']):
        """Apply a strftime expression to this column expression.

        Strftime will take a date or datetime value to a string/int value given a format string.

        Args:
            dt_format (Union[str, BaseColumnExpression]): datetime format string to supply to strftime. Can be a python
            string literal or a string-valued column expression.

        Returns:
            Strftime: Strftime instance representing the expression applied to this column.
        """
        from ..column_op.binary_op import Strftime
        return Strftime(dt_format, self)

    def to_date(self):
        """Apply a To_Date expression to this column expression.

        To_Date will take a string value to a datetime value.

        Returns:
            ToDate: ToDate instance representing the expression applied to this column.
        """
        from ..column_op.unary_op import ToDate
        return ToDate(self)

    def unixepoch(self):
        """Apply a strftime expression returns the unix epoch of a datetime-valued column expression.

        Returns:
            Strftime: Strftime instance representing the expression applied to this column.
        """
        return self.strftime('%s')

