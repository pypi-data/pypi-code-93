from stackifyapm.instrumentation.decorators import call_exception_handler
from stackifyapm.instrumentation.packages.dbapi2 import (
    ConnectionProxy,
    CursorProxy,
    DbApi2Instrumentation,
)


class PyODBCCursorProxy(CursorProxy):
    provider_name = "pyodbc"


class PyODBCConnectionProxy(ConnectionProxy):
    cursor_proxy = PyODBCCursorProxy


class PyODBCInstrumentation(DbApi2Instrumentation):
    name = "pyodbc"

    instrument_list = [("pyodbc", "connect")]

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        return PyODBCConnectionProxy(wrapped(*args, **kwargs))
