from stackifyapm.instrumentation.decorators import call_exception_handler
from stackifyapm.instrumentation.packages.dbapi2 import (
    ConnectionProxy,
    CursorProxy,
    DbApi2Instrumentation,
)
from stackifyapm.utils import default_ports


class MySQLCursorProxy(CursorProxy):
    provider_name = "mysql"


class MySQLConnectionProxy(ConnectionProxy):
    cursor_proxy = MySQLCursorProxy


class MySQLInstrumentation(DbApi2Instrumentation):
    name = "mysql"
    host = None

    instrument_list = [("MySQLdb", "connect"), ('flaskext.mysql', 'MySQL.connect')]

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        meta_data = {
            "host": args[0] if len(args) else kwargs.get("host", "localhost"),
            "port": args[4] if len(args) > 4 else int(kwargs.get("port", default_ports.get("mysql"))),
        }
        return MySQLConnectionProxy(wrapped(*args, **kwargs), meta_data=meta_data)
