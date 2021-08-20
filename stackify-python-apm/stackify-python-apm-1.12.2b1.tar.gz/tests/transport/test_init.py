from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.base import Client
from stackifyapm.traces import Transaction
from stackifyapm.transport import Transport
from stackifyapm.transport import TransportTypes
from stackifyapm.transport.agent import AgentSocketTransport
from stackifyapm.transport.default import DefaultTransport
from stackifyapm.transport.http import AgentHTTPTransport
from stackifyapm.transport.logger import LoggingTransport
from stackifyapm.utils.disttracing import TraceParent

CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
    "ASYNC_MODE": False,
}


class TransportTypesTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        self.trace_parent = TraceParent("2.0", "some_id", None)

    def test_transport_types(self):
        assert TransportTypes.AGENT_HTTP == 'agent_http'
        assert TransportTypes.AGENT_SOCKET == 'agent_socket'
        assert TransportTypes.DEFAULT == 'default'
        assert TransportTypes.LOGGING == 'logging'

    def test_get_transport_with_default(self):
        transport = TransportTypes.get_transport(self.client)

        assert isinstance(transport, DefaultTransport)

    def test_get_transport_with_socket_agent(self):
        self.client.config.transport = 'agent_socket'

        transport = TransportTypes.get_transport(self.client)

        assert isinstance(transport, AgentSocketTransport)

    def test_get_transport_with_http_agent(self):
        self.client.config.transport = 'agent_http'

        transport = TransportTypes.get_transport(self.client)

        assert isinstance(transport, AgentHTTPTransport)

    def test_get_transport_with_logging(self):
        self.client.config.transport = 'logging'

        transport = TransportTypes.get_transport(self.client)

        assert isinstance(transport, LoggingTransport)


class TransportTest(TestCase):
    def setUp(self):
        self.trace_parent = TraceParent("2.0", "some_id", None)

    def test_log_with_socket_agent(self):
        CONFIG["TRANSPORT"] = "agent_socket"
        client = Client(CONFIG)
        transaction = Transaction("request", self.trace_parent, meta_data=client.get_meta_data())
        transaction.end_transaction()
        transport = Transport(client)

        transport.handle_transaction(transaction)

        assert len(transport.transport.traces.traces) == 1

    def test_log_with_http_agent(self):
        CONFIG["TRANSPORT"] = "agent_http"
        client = Client(CONFIG)
        transaction = Transaction("request", self.trace_parent, meta_data=client.get_meta_data())
        transaction.end_transaction()
        transport = Transport(client)

        transport.handle_transaction(transaction)

        assert len(transport.transport.traces.traces) == 1

    @mock.patch('logging.StreamHandler.emit')
    def test_log_with_logging(self, emit_mock):
        CONFIG["TRANSPORT"] = "logging"
        CONFIG["LAMBDA_HANDLER"] = "test"

        client = Client(CONFIG)
        transaction = Transaction("request", self.trace_parent, meta_data=client.get_meta_data())
        transaction.end_transaction()
        transport = Transport(client)

        transport.handle_transaction(transaction)

        assert emit_mock.called
