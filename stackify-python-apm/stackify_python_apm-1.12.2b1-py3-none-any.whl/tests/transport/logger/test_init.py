import base64
import json
import logging
import gzip
from unittest import TestCase

try:
    from unittest import mock
except Exception:
    import mock

try:
    from cStringIO import StringIO
except Exception:
    try:
        from StringIO import StringIO
    except Exception:
        pass  # python 3, we use a new function in gzip

from stackifyapm.base import Client
from stackifyapm.traces import Transaction
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
    "TRANSPORT": 'logging',
    "LAMBDA_HANDLER": "test"
}


def get_transaction_from_log_data(data):
    b64_data = base64.b64decode(data)

    if hasattr(gzip, 'decompress'):
        return gzip.decompress(b64_data).decode("utf-8")
    else:
        sio = StringIO()
        sio.write(b64_data)
        sio.seek(0)
        g = gzip.GzipFile(fileobj=sio, mode='rb')
        transaction = g.read()
        g.close()
        return transaction.decode("utf-8")


class AgentLoggerTransportTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        self.trace_parent = TraceParent("2.0", "some_id", None)
        self.transport = LoggingTransport(client=self.client)

    def test_handler(self):
        assert self.transport.logging.handlers
        assert logging.StreamHandler in [handler.__class__ for handler in self.transport.logging.handlers]

    @mock.patch('logging.StreamHandler.emit')
    def test_log_transaction(self, emit_mock):
        transaction = Transaction("request", self.trace_parent, meta_data=self.client.get_meta_data())
        transaction.end_transaction()

        self.transport.log_transaction(transaction)

        assert emit_mock.called

    @mock.patch('logging.StreamHandler.emit')
    def test_log_data(self, emit_mock):
        transaction = Transaction("request", self.trace_parent, meta_data=self.client.get_meta_data())
        transaction.end_transaction()

        self.transport.log_transaction(transaction)

        assert emit_mock.called

        data = get_transaction_from_log_data(emit_mock.call_args[0][0].msg)
        transaction_data = json.loads(data)

        assert transaction_data['id'] == transaction.get_id()


class AgentLoggerTransportRootTest(TestCase):
    def setUp(self):
        CONFIG.pop("LAMBDA_HANDLER", None)
        self.client = Client(CONFIG)
        self.trace_parent = TraceParent("2.0", "some_id", None)
        self.transport = LoggingTransport(client=self.client)

    @mock.patch('logging.info')
    def test_log_transaction(self, info_mock):
        transaction = Transaction("request", self.trace_parent, meta_data=self.client.get_meta_data())
        transaction.end_transaction()

        self.transport.log_transaction(transaction)

        assert info_mock.called

    @mock.patch('logging.info')
    def test_log_data(self, info_mock):
        transaction = Transaction("request", self.trace_parent, meta_data=self.client.get_meta_data())
        transaction.end_transaction()

        self.transport.log_transaction(transaction)

        assert info_mock.called

        data = get_transaction_from_log_data(info_mock.call_args[0][0][16:])
        transaction_data = json.loads(data)

        assert transaction_data['id'] == transaction.get_id()
