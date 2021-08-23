from __future__ import annotations

from typing import Any, Collection, Mapping, Optional

from atoti._docs_utils import TABLE_CREATION_KWARGS, doc
from atoti._java_api import JavaApi
from atoti._jdbc_utils import normalize_jdbc_url
from atoti._sources import DataSource
from atoti.session import Session, _CreateTablePrivateParameters
from atoti.table import Table
from atoti.type import DataType

from .drivers import _infer_driver

SQL_KWARGS = {
    "url": """url: The JDBC connection URL of the database.
            The ``jdbc:`` prefix is optional but the database specific part (such as ``h2:`` or ``mysql:``) is mandatory.
            For instance:

                * ``h2:file:/home/user/database/file/path;USER=username;PASSWORD=passwd``
                * ``mysql://localhost:7777/example?user=username&password=passwd``
                * ``postgresql://postgresql.db.server:5430/example?user=username&password=passwd``

            More examples can be found `here <https://www.baeldung.com/java-jdbc-url-format>`__.""",
    "query": """query: The result of this SQL query will be loaded into the table.""",
    "driver": """driver: The JDBC driver used to load the data.
            If ``None``, the driver is inferred from the URL.
            Drivers can be found in the :mod:`atoti_sql.drivers` module.""",
}


def create_source_params(
    *,
    query: str,
    url: str,
    driver: str,
) -> Mapping[str, Any]:
    """Create the SQL specific parameters."""
    return {
        "query": query,
        "url": url,
        "driverClass": driver,
    }


class SqlDataSource(DataSource):
    """SQL data source."""

    def __init__(self, java_api: JavaApi):
        """Init."""
        super().__init__(java_api, "JDBC")

    def load_sql_into_table(
        self,
        table: Table,
        *,
        scenario_name: Optional[str],
        url: str,
        query: str,
        driver: str,
    ):
        """Load the data from SQL database into the table."""
        source_params = create_source_params(
            query=query,
            url=url,
            driver=driver,
        )
        self.load_data_into_table(
            table.name,
            scenario_name=scenario_name,
            source_params=source_params,
        )

    def infer_sql_types(
        self,
        *,
        keys: Optional[Collection[str]],
        url: str,
        query: str,
        driver: str,
    ):
        """Infer Table types from the SQL database."""
        source_params = create_source_params(
            query=query,
            url=url,
            driver=driver,
        )
        return self._java_api.infer_table_types_from_source(
            source_key=self.source_key,
            keys=keys,
            source_params=source_params,
        )


@doc(**{**TABLE_CREATION_KWARGS, **SQL_KWARGS})
def read_sql(
    self: Session,
    query: str,
    *,
    url: str,
    table_name: str,
    driver: Optional[str] = None,
    keys: Optional[Collection[str]] = None,
    partitioning: Optional[str] = None,
    types: Optional[Mapping[str, DataType]] = None,
    hierarchized_columns: Optional[Collection[str]] = None,
    **kwargs: Any,
) -> Table:
    """Create a table from the result of the passed SQL query.

    Note:
        This method requires the :mod:`atoti-sql <atoti_sql>` plugin.

    Args:
        {query}
        {url}
        {driver}
        {table_name}
        {keys}
        {partitioning}
        types: Types for some or all columns of the table.
            Types for non specified columns will be inferred from the SQL types.
        {hierarchized_columns}

    Example:
        .. doctest:: read_sql

            >>> table = session.read_sql(
            ...     "SELECT * FROM MYTABLE;",
            ...     url=f"h2:file:{{RESOURCES}}/h2-database;USER=root;PASSWORD=pass",
            ...     table_name="Cities",
            ...     keys=["ID"],
            ... )
            >>> len(table)
            5

        .. doctest:: read_sql
            :hide:

            Remove the edited H2 database from Git's working tree.
            >>> session.close()
            >>> import os
            >>> os.system(f"git checkout -- {{RESOURCES}}/h2-database.mv.db")
            0

    """
    private_parameters = _CreateTablePrivateParameters(**kwargs)
    url = normalize_jdbc_url(url)
    inferred_types = SqlDataSource(self._java_api).infer_sql_types(
        keys=keys,
        url=url,
        query=query,
        driver=driver or _infer_driver(url),
    )
    types = {**inferred_types, **types} if types is not None else inferred_types
    table = self.create_table(
        table_name,
        types=types,
        keys=keys,
        partitioning=partitioning,
        hierarchized_columns=hierarchized_columns,
        columns_with_shared_dictionary=private_parameters.columns_with_shared_dictionary,
    )
    load_sql(table, query, url=url, driver=driver)
    return table


@doc(
    **{
        **SQL_KWARGS,
        # Declare the types here because blackdoc and doctest conflict when inlining it in the docstring.
        "types": """{"ID": tt.type.INT, "CITY": tt.type.STRING, "MY_VALUE": tt.type.NULLABLE_DOUBLE}""",
    }
)
def load_sql(
    self: Table,
    query: str,
    *,
    url: str,
    driver: Optional[str] = None,
):
    """Load the result of the passed SQL query into the table.

    Note:
        This method requires the :mod:`atoti-sql <atoti_sql>` plugin.

    Args:
        {query}
        {url}
        {driver}

    Example:
        .. doctest:: load_sql

            >>> table = session.create_table("Cities", types={types}, keys=["ID"])
            >>> table.load_sql(
            ...     "SELECT * FROM MYTABLE;",
            ...     url=f"h2:file:{{RESOURCES}}/h2-database;USER=root;PASSWORD=pass",
            ... )
            >>> len(table)
            5

        .. doctest:: read_sql
            :hide:

            Remove the edited H2 database from Git's working tree.
            >>> session.close()
            >>> import os
            >>> os.system(f"git checkout -- {{RESOURCES}}/h2-database.mv.db")
            0
    """
    url = normalize_jdbc_url(url)
    SqlDataSource(self._java_api).load_sql_into_table(
        self,
        scenario_name=self.scenario,
        url=url,
        query=query,
        driver=driver or _infer_driver(url),
    )
