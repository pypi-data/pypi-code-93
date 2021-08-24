from itertools import combinations
from enum import Enum


class SqlValType(Enum):
    Int = 0
    Decimal = 1
    Double = 2
    Text = 3
    DateTime = 4
    Date = 5
    Boolean = 6
    Table = 7
    BigInt = 8

    ListInt = 9
    ListDecimal = 10
    ListDouble = 11
    ListText = 12
    ListDateTime = 13
    ListDate = 14
    ListBoolean = 15

    Column = 16
    ColumnSelection = 17
    TableDef = 18
    Parameter = 19
    Ordering = 20
    Grouping = 21
    ColumnIndex = 22

    Unit = 23
    Null = 24


all_types = [t for t in SqlValType]

numerics = [SqlValType.Int, SqlValType.Decimal, SqlValType.Double, SqlValType.BigInt]

column_types = [SqlValType.Int, SqlValType.Decimal, SqlValType.Double,
                SqlValType.Text, SqlValType.Date, SqlValType.DateTime,
                SqlValType.Boolean, SqlValType.BigInt]

# Should double always be comparable to the other numerics?
comparables = [set(pair) for pair in combinations(numerics, 2)] \
              + [{SqlValType.Date, SqlValType.DateTime}] \
              + [{col_type} for col_type in all_types]


list_type_pairs = [
    {SqlValType.Int, SqlValType.ListInt},
    {SqlValType.Decimal, SqlValType.ListDecimal},
    {SqlValType.Double, SqlValType.ListDouble},
    {SqlValType.Text, SqlValType.ListText},
    {SqlValType.DateTime, SqlValType.ListDateTime},
    {SqlValType.Date, SqlValType.ListDate},
    {SqlValType.Boolean, SqlValType.ListBoolean},
]

numeric_priority_dict = {
    SqlValType.Decimal: 1,
    SqlValType.Double: 2,
    SqlValType.BigInt: 3,
    SqlValType.Int: 4
}


def numeric_priority(x, y):

    if x not in numeric_priority_dict.keys() or y not in numeric_priority_dict.keys():
        raise ValueError("Unrecognised types for numeric bi-linear op type resolution.")

    if numeric_priority_dict[x] < numeric_priority_dict[y]:
        return x
    else:
        return y


def fixed_type(lumi_type):
    return lambda *args: lumi_type
