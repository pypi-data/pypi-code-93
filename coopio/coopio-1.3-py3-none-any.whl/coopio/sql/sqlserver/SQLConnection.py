import pyodbc
import logging

# SQL Server Native Client 11.0
# SQL Server Native Client RDA 11.0
# ODBC Client 13 for SQL Server
# ODBC Client 17 for SQL Server
# SQL Server

def connect(connectionString:str,
            loggingLevel=logging.DEBUG,
            context=None,
            login_timeout=0,
            autocommit: bool = False):
    try:
        logging.log(loggingLevel, f"Establishing connection to SQL Server. Context [{context}] -- {connectionString}")
        conn = pyodbc.connect(connectionString, timeout=login_timeout, autocommit=autocommit)

        logging.log(loggingLevel, f"Connection established! Context: [{context}]")
        return conn
    except pyodbc.InterfaceError as e:
        error = f"Context [{context}]: {e}"
        logging.error(error)
        raise Exception(error)
    except Exception as e:
        error = f"Context [{context}]: {e}"
        logging.error(error)
        raise Exception(error)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(name)s -- %(asctime)s : [%(levelname)s] %(message)s (%(filename)s lineno: %(lineno)d)')
    # sql_db_connection = "Driver={SQL Server Native Client 11.0};Server=192.168.11.4;Database=MaestroAnalytics;Trusted_Connection=no;UID=asapdb;PWD=asap;"
    sql_db_connection = r'Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=master;Trusted_Connection=yes;'
    conn = connect(connectionString=sql_db_connection, loggingLevel=logging.DEBUG, context="TEST")