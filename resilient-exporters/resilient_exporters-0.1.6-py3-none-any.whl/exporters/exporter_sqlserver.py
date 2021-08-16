import urllib
import logging
from typing import Text
from resilient_exporters import utils
from resilient_exporters.exporters import Exporter, ExportResult
from resilient_exporters.exceptions import MissingConfigError, \
                                           InvalidConfigError, \
                                           MissingModuleError, \
                                           ExportError

logger = logging.getLogger(__name__)

try:
    import _mssql
except ModuleNotFoundError:
    logger.error("""Module pymssql not available. Install using:
                    pip install resilient-exporters[sqlserver]""")
    raise
except ImportError as e:
    logger.error(e)
    logger.error("""Is FreeTDS installed in the system?""")
    raise

class SQLServerExporter(Exporter):
    """Exporter for Microsoft SQL Server, Azure SQL DB and MySQL.

    Args:
        target_host (str):
        target_port (int):
        username (str):
        password (str):
        database (str):
        default_table (str):
        create_table_if_inexistent (bool):
        **kwargs : the keyword arguments to pass down to parent's class Exporter
    Raises:
        InvalidConfigError: if it cannot retrieve the server information, which
            is likely due an invalid configuration of the target.

    .. admonition:: Example

        .. code-block:: python

            import os
            from resilient_exporters.exporters import SQLServerExporter

            exporter = SQLServerExporter(target_host="myserver.domain.net",
                                         username="username",
                                         password="my-password",
                                         database="profiles",
                                         default_table="scientists")

            data = {"name": "Richard Feynman",
                    "age": 69}
            exporter.send(data)
    """
    def __init__(self,
                 target_host: Text,
                 database: Text,
                 target_port: int = 1433,
                 username: Text = None,
                 password: Text = None,
                 default_table: Text = None,
                 **kwargs):
        super(SQLServerExporter, self).__init__(**kwargs)

        self.__conn = _mssql.connect(server=target_host, 
                                     user=username, 
                                     password=password, 
                                     database=database)

        self.__default_table = default_table

        # List tables in the database
        try:
            self.__conn.execute_query("SELECT * FROM INFORMATION_SCHEMA.TABLES")
            self.__all_tables = {}
            for row in self.__conn:
                self.__all_tables[row["TABLE_NAME"]] = {}
        except _mssql.MSSQLDataBaseException as e:
            logging.error(e)
            raise InvalidConfigError(self, "Cannot retrieve database info. Is \
                                            the configuration valid? Does the user have read rights?")
        
        # Get information on columns for each table
        for table_name in self.__all_tables.keys():
            self.__conn.execute_query(f"""SELECT COLUMN_NAME, DATA_TYPE, ORDINAL_POSITION, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, DATETIME_PRECISION FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{table_name}'""")
            for col in self.__conn:
                if col["CHARACTER_MAXIMUM_LENGTH"]:
                    precision = col["CHARACTER_MAXIMUM_LENGTH"]
                elif col["NUMERIC_PRECISION"]:
                    precision = col["NUMERIC_PRECISION"]
                else:
                    precison = col["DATETIME_PRECISION"]

                col_info = (col["DATA_TYPE"], col["ORDINAL_POSITION"], col["IS_NULLABLE"], precision)

                self.__all_tables[table_name][col["COLUMN_NAME"]] = col_info

    def send(self,
             data: dict,
             table: Text = None) -> ExportResult:
        """Inserts data into a table. Reuses default database and
        tables names, if provided at initialisation.

        Args:
            data (dict): a dict representing the document to insert into the
                collection.
            table (str): name of the target table. If `None`, will use
                the default value. Default is `None`.

        Returns:
            ExportResult: the result in the form (ObjectId, True) if successful,
                (None, False) otherwise.

        Raises:
            MissingConfigError: if it cannot find a database and/or collection
                in the arguments and default values.
        """
        if table is None:
            if self.__default_table is None:
                    logger.error("""No table name given and no default table 
                                    configured.""")
                    raise MissingConfigError(self, """No table given by 
                            argument nor default table configured. Please 
                            provide a table name.""")
            table = self.__default_table

        if table in self.__all_tables.keys():
            # Validates the data, raises errors in case something is wrong
            utils.validate_data_for_sql_table(data, self.__all_tables[table])
            
            columns = ",".join(data.keys())
            values = ",".join([ f"'{val}'" if isinstance(val, str) else str \
                                                (val) for val in data.values()])

            self.__conn.execute_non_query(f"""INSERT INTO {table}({columns})
                                              VALUES({values})""", table)
            return ExportResult(None, True)
        else:
            logger.error(f"Invalid table name provided: {table}")
            raise InvalidConfigError(self, f"""Table {table} does not exist in
                                                database. Provide the name of 
                                                an existing table""")
                                            