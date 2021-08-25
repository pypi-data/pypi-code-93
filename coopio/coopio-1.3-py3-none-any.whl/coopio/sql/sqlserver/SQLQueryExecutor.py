from coopio.sql.SqlReturnObj import SqlReturnObj
import time
import logging
import coopio.sql.sqlserver.SQLConnection as SQLConnection
import pandas as pd
from typing import Callable
import coopio.sql.SQLLogging as slog

def execute_sql(sql: str,
                connection_string_provider: Callable[[], str],
                autocommit: bool = False,
                title: str = None) -> SqlReturnObj:
    slog.init_logging_config()

    start_time = time.perf_counter()
    # logging.log(QUERY, f"Running the {title} query\n")
    title_txt = f"the {title}" if title is not None else "a "
    logging.query(f"Running {title_txt} query\n")

    error = None
    myData = None
    try:
        connection_string = connection_string_provider()
        conn = SQLConnection.connect(connectionString=connection_string, loggingLevel=logging.DEBUG, context=title, autocommit=autocommit)

        cursor = conn.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        print(data)
        myData = pd.DataFrame(data)

        # myData = pd.read_sql(sql, conn)
        logging.query(f"Data Returned for {title}: \n\t{myData}"
                                         f"\n\tusing the query:"
                                         f"\n\t\"{sql}\"")
    except Exception as e:
        logging.error(f"Unable to return data from source: {e}, {type(e)}")
        error = e
        myData = None
    finally:
        end_time = time.perf_counter()
        return SqlReturnObj(error=error, data=myData, timer=f"{(end_time - start_time):.4f} sec")

if __name__ == "__main__":
    import coopio.sql.SQLLogging as slog
    slog.init_logging_config()
    logging.basicConfig(level=logging.DEBUG)
    connection_string_provider = lambda: r'Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=master;Trusted_Connection=yes;'

    execute_sql("CREATE DATABASE testdb", "Create test database", connection_string_provider)

