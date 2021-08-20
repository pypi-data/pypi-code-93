from stackifyapm.instrumentation.decorators import call_exception_handler
from stackifyapm.instrumentation.packages.dbapi2 import (
    ConnectionProxy,
    CursorProxy,
    DbApi2Instrumentation,
)
from stackifyapm.utils import default_ports


class PyMSSQLCursorProxy(CursorProxy):
    provider_name = "pymssql"


class PyMSSQLConnectionProxy(ConnectionProxy):
    cursor_proxy = PyMSSQLCursorProxy


class PyMSSQLInstrumentation(DbApi2Instrumentation):
    name = "pymssql"

    instrument_list = [("pymssql", "connect")]

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        host = args[0] if args else kwargs.get("server")
        port = None

        if not host:
            host = kwargs.get("host", "localhost")
            for sep in (",", ":"):
                if sep in host:
                    host, port = host.rsplit(sep, 1)
                    port = int(port)
                    break

        if not port:
            port = int(kwargs.get("port", default_ports.get("mssql")))

        meta_data = {
            "host": host,
            "port": port,
        }

        return PyMSSQLConnectionProxy(wrapped(*args, **kwargs), meta_data=meta_data)
