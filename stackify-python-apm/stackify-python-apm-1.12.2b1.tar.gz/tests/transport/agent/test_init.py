from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.base import Client
from stackifyapm.conf.constants import AGENT_TRACES_MAX_SIZE
from stackifyapm.traces import Transaction
from stackifyapm.transport.agent import AgentSocketTransport
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
    "TRANSPORT": 'agent_socket',
}


class AgentSocketTransportTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        self.trace_parent = TraceParent("2.0", "some_id", None)
        self.transport = AgentSocketTransport(self.client)

    def shutDown(self):
        self.transport.timer.stop()

    def test_debug(self):
        self.transport.timer.stop()
        transaction = Transaction("request", self.trace_parent, meta_data=self.client.get_meta_data())
        transaction.end_transaction()

        self.transport.log_transaction(transaction)

        assert len(self.transport.traces.traces) == 1

    @mock.patch('requests_unixsocket.Session.post')
    def test_send_all(self, mock_post):
        self.transport.timer.stop()
        transaction = Transaction("request", self.trace_parent, meta_data=self.client.get_meta_data())
        transaction.end_transaction()
        self.transport.log_transaction(transaction)

        self.transport.send_all()

        assert mock_post.called

    @mock.patch('requests_unixsocket.Session.post')
    def test_max_message_length(self, mock_post):
        self.transport.timer.stop()

        for i in range(AGENT_TRACES_MAX_SIZE):
            transaction = Transaction("request", self.trace_parent, meta_data=self.client.get_meta_data())
            transaction.end_transaction()
            self.transport.log_transaction(transaction)

        assert mock_post.called
