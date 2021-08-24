from decimal import Decimal

from lumipy.query.expression.base_expression import BaseExpression
from datetime import datetime, date
from .column_base import BaseColumnExpression
from lumipy.common.string_utils import sql_str_to_name
from typing import Union

from lumipy.navigation.field_metadata import FieldMetadata
from ..sql_value_type import SqlValType


def python_to_expression(
        value: Union[int, Decimal, float, str, datetime, date, bool, BaseExpression]
) -> BaseExpression:
    """Convert a python primitive to LiteralColumn if the input value is a python primitive, else pass expression
    through.

    Args:
        value (Union[int, Decimal, float, str, datetime, date, bool, List, BaseColumnExpression]): input value to
        (possibly) convert to LiteralColumn.

    Returns:
        BaseColumnExpression: either the original column expression or the literal as LiteralColumn.
    """
    if not issubclass(type(value), BaseExpression):
        return LiteralColumn(value)
    else:
        return value


def _primitive_to_str(x: Union[str, int, float, Decimal, datetime, date, list, bool]):
    """Convert a python primitive value to its SQL string counterpart.
    This handles extra chars that might need adding for the syntax such as '' around string literals
    or ## around datetime literals.

    Args:
        x (Union[str, int, float, Decimal, datetime, date, list, bool]): input python primitive value

    Returns:
        str: SQL string piece counterpart.
    """
    if type(x) == str:
        return f"'{x}'"
    if type(x) == datetime:
        date_str = x.strftime('%Y-%m-%d %H:%M:%S.%f')
        return f"#{date_str}#"
    if type(x) == date:
        date_str = x.strftime('%Y-%m-%d')
        return f"#{date_str}#"
    if type(x) == type(None):
        return "null"
    else:
        # Otherwise normal python str conversion is ok
        return str(x)


class LiteralColumn(BaseColumnExpression):
    """Column expression that represents literal values in statements such as select (e.g. select 3.14 from table).

    """

    def __init__(self, values: Union[int, Decimal, float, str, datetime, date, bool]):
        """__init__ method for the LiteralColumn class.

        Args:
            values (Union[int, Decimal, float, str, datetime, date, bool]): python literal to convert to
            LiteralColumn.
        """

        type_sig = type(values)
        type_description = f"{type(values).__name__}"

        # Check primitive type is supported
        if type_sig not in py_type_to_lumi_data_type.keys():
            raise ValueError(
                f"Python type [{type_description}] is not supported in assignment expressions."
            )

        # Make a dummy field description
        name = 'const_' + sql_str_to_name(_primitive_to_str(values))
        field_description = FieldMetadata(
            field_name=_primitive_to_str(values),
            field_type='Column',
            table_name='literal_input',
            data_type=py_type_to_lumi_data_type[type_sig],
            description="literal value",
            is_main=False,
            is_primary_key=False,
            param_default_value=None,
            table_param_columns=None,
            name_override=name
        )

        self._py_value = values
        super().__init__(
            hash(field_description.table_name),
            lambda x: f"{x.field_name}",
            lambda x: True,
            lambda x: x,
            'literal',
            field_description
        )

    def get_py_value(self):
        return self._py_value

    def __hash__(self):
        return hash(self.get_sql())


py_type_to_lumi_data_type = {
    int: SqlValType.Int,
    Decimal: SqlValType.Decimal,
    float: SqlValType.Double,
    str: SqlValType.Text,
    datetime: SqlValType.DateTime,
    date: SqlValType.Date,
    bool: SqlValType.Boolean,
    type(None): SqlValType.Null,

    (list, int): SqlValType.ListInt,
    (list, Decimal): SqlValType.ListDecimal,
    (list, float): SqlValType.ListDouble,
    (list, str): SqlValType.ListText,
    (list, datetime): SqlValType.ListDateTime,
    (list, date): SqlValType.ListDate,
    (list, bool): SqlValType.ListBoolean,
}
