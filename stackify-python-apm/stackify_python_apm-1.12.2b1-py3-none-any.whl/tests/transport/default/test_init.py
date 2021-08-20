import os
from unittest import TestCase

from stackifyapm.base import Client
from stackifyapm.conf.constants import LOG_PATH
from stackifyapm.traces import Transaction
from stackifyapm.transport.default import DefaultTransport
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


class DefaultTransportTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        self.trace_parent = TraceParent("2.0", "some_id", None)
        self.transport = DefaultTransport(self.client)

    def test_log_transaction(self):
        client = Client(CONFIG)
        host_name = client.get_system_info().get("hostname")
        process_id = client.get_process_info().get("pid")
        filename = "{}{}#{}-1.log".format(LOG_PATH, host_name, process_id)

        transaction = Transaction("request", self.trace_parent, meta_data=self.client.get_meta_data())
        transaction.end_transaction()

        try:
            self.transport.log_transaction(transaction)

            assert os.path.exists(filename)
        except AttributeError as e:
            assert str(e) == "'NoneType' object has no attribute 'debug'"

        try:
            os.path.exists(filename) and os.remove(filename)
        except Exception:
            # we cant delete file in use on windows machine
            pass
