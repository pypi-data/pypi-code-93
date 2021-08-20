from stackifyapm.exceptions import StackifyAPMException
from stackifyapm.instrumentation.decorators import call_exception_handler
from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.utils import compat
from stackifyapm.utils.helper import is_async_span


class CassandraInstrumentation(AbstractInstrumentedModule):
    name = "cassandra"

    instrument_list = [
        ("cassandra.cluster", "Session.execute"),
        ("cassandra.cluster", "Cluster.connect"),
    ]

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        try:
            context = {
                "CATEGORY": "Cassandra",
            }
            if method == "Cluster.connect":
                kind = "db.cassandra.connect"
                context["SUBCATEGORY"] = "Connect"

                # < cassandra-driver 3.18
                if hasattr(instance, "contact_points_resolved"):
                    host = instance.contact_points_resolved[0]
                    port = instance.port
                else:
                    host = instance.endpoints_resolved[0].address
                    port = instance.endpoints_resolved[0].port
            else:
                kind = "db.cassandra.query"
                query = args[0] if args else kwargs.get("query")

                hosts = list(instance.hosts)
                if hasattr(hosts[0], "endpoint"):
                    host = hosts[0].endpoint.address
                    port = hosts[0].endpoint.port
                else:
                    # < cassandra-driver 3.18
                    host = hosts[0].address
                    port = instance.cluster.port

                if hasattr(query, "query_string"):
                    query_str = query.query_string
                elif hasattr(query, "prepared_statement") and hasattr(query.prepared_statement, "query"):
                    query_str = query.prepared_statement.query
                elif isinstance(query, compat.string_types):
                    query_str = query
                else:
                    query_str = None
                if query_str:
                    context["SUBCATEGORY"] = "Execute"
                    context["SQL"] = query_str

            context['URL'] = '{}:{}'.format(host, port)
        except Exception as e:
            raise StackifyAPMException(e)

        with CaptureSpan(kind, context, is_async=is_async_span()):
            return wrapped(*args, **kwargs)
