import pyodbc
import logging
import pandas as pd
import time

from coopio.sql.SqlReturnObj import SqlReturnObj
from coopio.DataAccessExecutor import DataAccessExecutor
from abc import ABC, abstractmethod
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, as_completed, ThreadPoolExecutor
from concurrent.futures._base import TimeoutError
from typing import Callable
from coopio.sql.sqlserver.SQLConnection import connect


class ExecuteArgs:
    def __init__(self, inargs, requestargs, context, query_timeout, login_timeout, connection_string_provider):
        self.inargs = inargs
        self.requestargs = requestargs
        self.context = context
        self.query_timeout=query_timeout
        self.login_timeout = login_timeout
        self.connection_string_provider =connection_string_provider

class SqlSpExecutor(DataAccessExecutor, ABC):
    def __init__(self, spName, sqlConnectionFunc, loggingLvl = logging.DEBUG):
        super().__init__(spName, loggingLvl)
        self.spName = spName
        self.sqlConnectionFunc = sqlConnectionFunc
        self.loggingLvl = loggingLvl

    @abstractmethod
    def _defineInputArgs(self):
        pass

    def _defineRequestArgs(self):
        pass

    def request(self, inargs, requestargs, context, query_timeout=0, login_timeout=0, execution_timeout=None, connection_string_provider:Callable[[], str]=None) -> SqlReturnObj:
        start_time = time.perf_counter()

        if connection_string_provider is None:
            logging.error("Connection String provider must be provided.")
            return

        with ThreadPoolExecutor() as executor:
            args_set = [ExecuteArgs(inargs=inargs, requestargs=requestargs, context=context,
                          query_timeout=query_timeout, login_timeout=login_timeout, connection_string_provider=connection_string_provider)]
            results = executor.map(self._connect_and_execute, args_set, timeout=execution_timeout)
            try:
                for result in results:
                    ret = result
            except TimeoutError as e:
                error = f"{type(e)}: Execution took longer than provided execution_timeout [{execution_timeout}], aborted. "
                logging.error(error)
                self.stop_waiting_for_threads(executor)
                ret = SqlReturnObj(error=error, callback=self._buildSP(inargs),
                                       return_type=inargs.get('return_type', None))
            except Exception as e:
                error = f"{type(e)}: Other error, aborted - {e}"
                logging.error(error)
                self.stop_waiting_for_threads(executor)
                ret = SqlReturnObj(error=error, callback=self._buildSP(inargs),
                                       return_type=inargs.get('return_type', None))
            finally:
                end_time = time.perf_counter()
                ret.timer = f"{(end_time - start_time):.4f} sec"
                logging.debug(f"Done with SQL execution, returning: {ret}")
                return ret

    def stop_waiting_for_threads(self, executor):
        import atexit
        atexit.unregister(concurrent.futures.thread._python_exit)
        executor.shutdown = lambda wait: None

    def _connect_and_execute(self, args: ExecuteArgs) -> SqlReturnObj:
        inargs = args.inargs if args.inargs else {}
        error = None
        sql = ""
        try:
            # Establish SQL CONNECTION
            connectionString = args.connection_string_provider()
            if connectionString is None:
                raise Exception("No Connection String provided")

            conn = connect(connectionString, self.loggingLevel, context=self.spName, login_timeout=args.login_timeou)

            if args.query_timeout is not None and isinstance(args.query_timeout, int) and args.query_timeout > 0:
                conn.timeout = 5

            if conn is None:
                raise Exception("Unable to connect to sql data source.")

            sql = self._buildSP(inargs)

            logging.log(self.loggingLvl, f"[{args.context}]: Running sql query: [{self.label}]")
            mydata = pd.read_sql(sql, conn)

            # print data that was returned
            with pd.option_context('display.max_columns', 2000, 'display.width', 250):
                logging.log(self.loggingLvl, f"[{args.context}]: [{self.label}] retrieved data {len(mydata)} row(s): "
                                             f"\n\t{mydata.describe(include='all')} "
                                             f"\n\t{mydata}"
                                             f"\n\t using query:"
                                             f"\n\t\"{sql}\"")

            ret = mydata
        except pyodbc.InterfaceError as e:
            logging.error(f"[{args.context}]:[{self.label}]: {e}")
            ret = None
        except Exception as e:
            logging.error(f"[{args.context}]:[{self.label}]: Unknown Error running {sql}: {e}")
            ret = None
            error = e
        finally:
            ret = SqlReturnObj(data=ret, return_type=inargs.get('return_type', None)
                                   , callback=sql, error=error)
            return ret

    def _buildSP(self, kwargs):
        # Define and run SQL Script
        sql = f"exec " + self.spName

        count = 0
        for kwarg in kwargs:
            if count != 0:
                sql += ","
            sql += f" @{kwarg} = '{kwargs[kwarg]}'"
            count += 1

        return sql

if __name__ == "__main__":
    se = SqlSpExecutor()
    se.run()