from unittest import TestCase

from stackifyapm.base import Client
from stackifyapm.conf.constants import AGENT_TRACES_MAX_SIZE
from stackifyapm.traces import Transaction
from stackifyapm.transport.base import BaseTransport
from stackifyapm.transport.base import ProtobufTransport
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


class BaseTransportTest(TestCase):
    def setUp(self):
        self.transport = BaseTransport()

    def test_log_transaction(self):
        self.assertRaises(NotImplementedError, self.transport.log_transaction, 'test')

    def test_send_all(self):
        self.assertRaises(NotImplementedError, self.transport.send_all)


class ProtobufTransportTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        self.trace_parent = TraceParent("2.0", "some_id", None)
        self.transport = ProtobufTransport()

    def shutDown(self):
        self.transport.timer.stop()

    def test_timer_started(self):
        assert self.transport.timer._started

    def test_log_transaction(self):
        self.transport.timer.stop()
        transaction = Transaction("request", self.trace_parent, meta_data=self.client.get_meta_data())
        transaction.end_transaction()

        self.transport.log_transaction(transaction)

        assert len(self.transport.traces.traces) == 1

    def test_send_all(self):
        self.transport.timer.stop()
        transaction = Transaction("request", self.trace_parent, meta_data=self.client.get_meta_data())
        transaction.end_transaction()
        self.transport.log_transaction(transaction)

        self.assertRaises(NotImplementedError, self.transport.send_all)

    def test_max_message_length(self):
        self.transport.timer.stop()

        with self.assertRaises(NotImplementedError):
            for i in range(AGENT_TRACES_MAX_SIZE):
                transaction = Transaction("request", self.trace_parent, meta_data=self.client.get_meta_data())
                transaction.end_transaction()
                self.transport.log_transaction(transaction)
