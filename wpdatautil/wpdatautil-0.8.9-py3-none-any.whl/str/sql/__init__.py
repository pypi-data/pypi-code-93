"""str SQL utilities."""
import functools
import textwrap
from typing import Dict, List, Optional


class SqlQuery:
    """SQL query helper to apply transformations to input columns, returning the output columns and query."""

    def __init__(self, inputs: List[str], *, transformations: Dict[str, Optional[str]], template: str, indent: int = 0) -> None:
        """Return a SQL query object.

        :param inputs: Input column names.
        :param transformations: Applicable transformations to input columns. If a column is to be transformed, its name is the key and its value is the transformation.
                                In the value, {col} is replaced with the respective column name. If the value is None, the column is skipped.
        :param template: SQL query to format. In it, {selections} is formatted with the actual selections.
        :param indent: The output query is indented by this number of spaces.

        Example: SqlQuery(['c1', 'c2', 'c3'],
                  transformations={'c2': None, 'c3': '{col} * 2', 'c4': 'count(*)'},
                  template=f'''SELECT {{selections}}
                               FROM t
                               ''',
                  indent=4 * 2)
        """
        self._inputs, self._transformations, self._template, self._indent = inputs, transformations, template, indent

    def __str__(self):
        return self.query

    @functools.cached_property
    def selections(self) -> Dict[str, str]:
        """Return the output column selections.

        Example: {'c1': 'c1', 'c3': 'c3 * 2', 'c4': 'count(*)'}
        """
        return sql_column_selections(self._inputs, transformations=self._transformations)

    @functools.cached_property
    def outputs(self) -> List[str]:
        """Return the output column names.

        Example: ['c1', 'c3', 'c4']
        """
        return list(self.selections)

    @functools.cached_property
    def query(self) -> str:
        """Return the formatted query.

        Example:
        -------
            SELECT
                c1,
                c3 * 2 AS c3,
                count(*) AS c4
            FROM t

        """
        query = self._template.format(selections=sql_column_selections_str(self.selections))
        query = textwrap.dedent(query).strip()
        query = textwrap.indent(query, prefix=" " * self._indent)
        return query.strip()


# Note: This function is deprecated. Use it via the SqlQuery class instead.
def sql_column_selections(inputs: List[str], *, transformations: Dict[str, Optional[str]]) -> Dict[str, str]:
    """Return a mapping of SQL SELECT clauses given the input columns after applying the given transformations.

    Example: sql_column_selections(['c1', 'c2', 'c3'], transformations={'c2': None, 'c3': '{col} * 2', 'c4': 'count(*)'}) -> {'c1': 'c1', 'c3': 'c3 * 2', 'c4': 'count(*)'}

    :param inputs: Input column names.
    :param transformations: Applicable transformations. If a column is to be transformed, its name is the key and its value is the transformation.
                            In the value, {col} is replaced with the respective column name. If the value is None, the column is skipped.
    """
    outputs = inputs + [c for c in transformations if c not in inputs]
    del inputs
    selections = {}

    for column_name in outputs:
        if column_name in transformations:
            transformed_column = transformations[column_name]
            if transformed_column is None:
                continue  # Skip column.
            transformed_column = transformed_column.format(col=column_name)
            selections[column_name] = transformed_column
        else:
            selections[column_name] = column_name

    return selections


# Note: This function is deprecated. Use it via the SqlQuery class instead.
def sql_column_selections_str(inputs: Dict[str, str]) -> str:
    """Return a string representation of a mapping of SQL SELECT clauses.

    Example: {'c1': 'c1', 'c2': 'c2 * 2'} -> 'c1, c2 * 2 AS c2'
    """
    return ", ".join(k if k == v else f"{v} AS {k}" for k, v in inputs.items())
