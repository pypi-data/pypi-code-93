from sqlalchemy import between, Column
from sqlalchemy.orm import Query

from cytra.db.inspection_mixin import InspectionMixin
from cytra.db.access_control_mixin import AccessControlMixin
from cytra.db.transform_mixin import TransformMixin
from cytra.exceptions import InvalidParamError


class FilteringMixin(TransformMixin, AccessControlMixin, InspectionMixin):
    """
    Filter a Sqlalchemy query by a `dict`

    Operators:

    - `!`   Not
    - `>=`  Greater than or Equal
    - `<=`  Less than or Equal
    - `>`   Greater than
    - `<`   Less than
    - `%~`  Case insensitive Like
    - `%`   Like
    - `^`   In, e.g: ^1,2,3
    - `!^`  Not In, e.g: !^1,2,3
    - `~`   Between, e.g: ~2018-05-29T11:23:16+04:30,2018-07-30T11:23:16+04:30

    Note: Without any operator means to Equal with keyword.
    Note: `LIKE` is case-insensitive by default in Sqlite

    Examples:

    where `name` is equal to `John`
    dict(name="John")

    where `age` is between `1` and `18`
    dict(age='~1,18')
    """

    @classmethod
    def filter_by_dict(cls, query: Query, criteria: dict) -> Query:
        for type_, key, info, col in cls.get_readables():
            if type_ == "relationships":
                continue
            json_name = cls.export_column_name(col_key=key, col_info=info)
            if json_name in criteria:
                value = criteria[json_name]
                query = cls._filter_by_column_value(query, col, value)

        return query

    @classmethod
    def filter_by_request(cls, query: Query) -> Query:
        return cls.filter_by_dict(query, cls.__app__.request.form)

    @classmethod
    def _filter_by_column_value(
        cls, query: Query, column: Column, value: str
    ) -> Query:
        import_value = getattr(cls, "import_value")
        if not isinstance(value, str):
            raise InvalidParamError

        if value.startswith("^") or value.startswith("!^"):
            value = value.split(",")
            not_ = value[0].startswith("!^")
            first_item = value[0][2 if not_ else 1 :]
            items = [first_item] + value[1:]
            items = [i for i in items if i.strip()]
            if not len(items):
                raise InvalidParamError("Invalid query string: %s" % value)
            expression = column.in_([import_value(column, j) for j in items])
            if not_:
                expression = ~expression

        elif value.startswith("~"):
            values = value[1:].split(",")
            start, end = [import_value(column, v) for v in values]
            expression = between(column, start, end)

        elif value == "null":
            expression = column.is_(None)
        elif value == "!null":
            expression = column.isnot(None)
        elif value.startswith("!"):
            expression = column != import_value(column, value[1:])
        elif value.startswith(">="):
            expression = column >= import_value(column, value[2:])
        elif value.startswith(">"):
            expression = column > import_value(column, value[1:])
        elif value.startswith("<="):
            expression = column <= import_value(column, value[2:])
        elif value.startswith("<"):
            expression = column < import_value(column, value[1:])
        elif value.startswith("%~"):
            expression = column.ilike(
                "%%%s%%" % import_value(column, value[2:])
            )
        elif value.startswith("%"):
            expression = column.like(
                "%%%s%%" % import_value(column, value[1:])
            )
        else:
            expression = column == import_value(column, value)

        return query.filter(expression)
