import logging
from typing import Text, Union
from ..exporters import Exporter, ExportResult
from ..utils import _validate_data_for_sql_table, \
                    _transform_data_for_sql_query, \
                    _describe_postgres_column
from ..exceptions import MissingConfigError, \
                         InvalidConfigError

logger = logging.getLogger(__name__)

try:
    import psycopg2
except ModuleNotFoundError:
    logger.error("""Module psycopg2 not available. Install using:
                    pip install resilient-exporters[postgres]""")
    raise


class PostgreSQLExporter(Exporter):
    """Exporter for PostgreSQL.

    Args:
        target_host (str):
        target_port (int):
        username (str):
        password (str):
        database (str):
        default_table (str):
        create_table_if_inexistent (bool): Default to False
        **kwargs : the keyword arguments to pass down to parent class Exporter
    Raises:
        InvalidConfigError: if it cannot retrieve the server information, which
            is likely due an invalid configuration of the target.

    .. admonition:: Example

        .. code-block:: python

            from resilient_exporters.exporters import PostgreSQLExporter

            exporter = PostgreSQLExporter(target_host="myserver.domain.net",
                                          username="username",
                                          password="my-password",
                                          database="profiles",
                                          default_table="scientists")

            data = {"name": "Richard Feynman",
                    "age": 69}
            exporter.send(data)
    """
    def __init__(self,
                 conn_string: Text = None,
                 target_host: Text = None,
                 database: Text = None,
                 target_port: int = 5432,
                 username: Text = None,
                 password: Text = None,
                 default_table: Text = None,
                 **kwargs):
        assert conn_string or (target_host and target_port), \
            "Either a connection string or target host is needed."
        super(PostgreSQLExporter, self).__init__(**kwargs)

        if conn_string:
            self.__conn = psycopg2.connect(conn_string)
        else:
            self.__conn = psycopg2.connect(host=target_host,
                                           port=target_port,
                                           user=username,
                                           password=password,
                                           dbname=database)
        self.__cur = self.__conn.cursor()
        self.__default_table = default_table

        # List tables in the database
        try:
            self.__cur.execute("SELECT * FROM pg_catalog.pg_tables \
                                WHERE schemaname != 'pg_catalog' \
                                AND schemaname != 'information_schema';")
            self.__all_tables = {}
            for row in self.__cur.fetchall():
                self.__all_tables[row[1]] = {}
        except Exception as e:
            logging.error(e)
            raise InvalidConfigError(self, "Cannot retrieve database info. \
                                            Is the configuration valid? \
                                            Does the user have read rights?")
        # Get information on columns for each table
        for tabname in self.__all_tables.keys():
            self.__cur.execute(f"SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, \
                                 ORDINAL_POSITION, IS_NULLABLE, \
                                 CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, \
                                 DATETIME_PRECISION FROM \
                                 information_schema.columns \
                                 WHERE table_name='{tabname}';")
            for col in self.__cur.fetchall():
                self.__all_tables[tabname][col[1]] = _describe_postgres_column(col)

    def send(self,
             data: Union[dict, tuple],
             table: Text = None,
             upsert_on: Union[Text, tuple, list] = None) -> ExportResult:
        """Inserts data into a table. Reuses default database and
        tables names, if provided at initialisation.

        Args:
            data (Union[dict, tuple]): a dict or tuple representing the
                document to insert into the collection. If a dict, the
                keys must be the column names. If a tuple, there must be
                as many elements as there are columns in the table.
            table (str): name of the target table. If `None`, will use
                the default value set at initialisation. Default is `None`.
            upsert_on (Union[Text, tuple, list]): upsert on given columns.
                If `None`, it will not do an upsert. Default is `None`.
        Returns:
            ExportResult: the result in the form (Object, True) if successful,
                (None, False) otherwise.

        Raises:
            MissingConfigError: if it cannot find a database and/or collection
                in the arguments and default values.
        """
        if table is None:
            if self.__default_table is None:
                raise MissingConfigError(self, "No table given by argument \
                                                nor default table configured.")
            table = self.__default_table

        if table in self.__all_tables.keys():
            # Validates the data, raises errors in case something is wrong
            _validate_data_for_sql_table(data, self.__all_tables[table])
            columns, values = _transform_data_for_sql_query(data)

            if isinstance(data, dict):
                query = f"INSERT INTO {table}({columns}) VALUES({values})"
            else:
                query = f"INSERT INTO {table} VALUES({values})"
            if upsert_on:
                if isinstance(upsert_on, str):
                    upsert_on = [upsert_on]
                if isinstance(upsert_on, list) \
                  or isinstance(upsert_on, tuple):
                    tmp = ""
                    for item in upsert_on:
                        assert item in columns, \
                            f"{item} is not a column of the table {table}"
                        tmp += item + ","
                    upsert_on = tmp[:-1]
                else:
                    raise InvalidConfigError("upsert_on type not supported")
                query += f" ON CONFLICT ({upsert_on}) DO UPDATE SET"
                for colname in columns.split(","):
                    if colname == upsert_on:
                        continue
                    query += f" {colname} = EXCLUDED.{colname},"
                query = query[:-1]  # removes last ',' character
            query += ";"
            logger.debug(f"Final query: {query}")
            try:
                self.__cur.execute(query, table)
                success = bool(self.__cur.rowcount)
                self.__conn.commit()
                return ExportResult(None, success)
            except psycopg2.Error as e:
                logging.error(e)
                return ExportResult(None, False)
        else:
            raise InvalidConfigError(self, f"Table {table} does not exist in \
                                            database. Provide the name of \
                                            an existing table")
