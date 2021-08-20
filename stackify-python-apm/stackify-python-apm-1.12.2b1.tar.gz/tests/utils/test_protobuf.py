import sys
from unittest import TestCase

from stackifyapm.base import Client
from stackifyapm.handlers.exceptions import get_exception_context
from stackifyapm.protos import stackify_trace_pb2
from stackifyapm.traces import Transaction
from stackifyapm.utils.disttracing import TraceParent
from stackifyapm.utils.protobuf import to_protobuf

CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
}


class ToProtobufTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)

    def test_to_protobuf(self):
        context = {
            "wrapped_method": "Execute",
            "provider": "postgres",
            "type": "Database",
            "sub_type": "database_sql",
            "statement": "Select * from sample",
        }
        trace_parent = TraceParent("2.0", "some_id", None)
        transaction = Transaction("request", trace_parent, meta_data=self.client.get_meta_data())
        transaction.begin_span("database", context=context, leaf=False)
        transaction.end_span()
        transaction.end_transaction()

        transaction_probuf = to_protobuf(transaction.to_dict())

        assert isinstance(transaction_probuf, stackify_trace_pb2.Trace)
        assert transaction_probuf.frame.properties
        assert transaction_probuf.frame.properties["CATEGORY"] == "Python"
        assert transaction_probuf.frame.properties["APPLICATION_FILESYSTEM_PATH"] == "path/to/application/"
        assert transaction_probuf.frame.properties["APPLICATION_NAME"] == "sample_application"
        assert transaction_probuf.frame.properties["APPLICATION_ENV"] == "production"
        assert len(transaction_probuf.frame.frames) == 1

    def test_to_probobuf_with_request_context(self):
        trace_parent = TraceParent("2.0", "some_id", None)
        transaction = Transaction("request", trace_parent, meta_data=self.client.get_meta_data())
        transaction.context = {
            "request": {
                "url": {
                    "pathname": "/somepath",
                    "full": "host.com/some_id",
                },
                "method": "get"
            }
        }
        transaction.end_transaction()

        transaction_probuf = to_protobuf(transaction.to_dict())

        assert transaction_probuf.frame.properties
        assert transaction_probuf.frame.properties["METHOD"] == "get"
        assert transaction_probuf.frame.properties["REPORTING_URL"] == "/somepath"
        assert transaction_probuf.frame.properties["URL"] == "host.com/some_id"

    def test_to_probobuf_with_response_context(self):
        trace_parent = TraceParent("2.0", "some_id", None)

        transaction = Transaction("request", trace_parent, meta_data=self.client.get_meta_data())
        transaction.context = {
            "response": {
                "status_code": 200,
            }
        }
        transaction.end_transaction()

        transaction_probuf = to_protobuf(transaction.to_dict())

        assert transaction_probuf.frame.properties
        assert transaction_probuf.frame.properties["STATUS"] == "200"

    def test_to_protobuf_multiple_span(self):
        trace_parent = TraceParent("2.0", "some_id", None)
        transaction = Transaction("request", trace_parent, meta_data=self.client.get_meta_data())
        transaction.begin_span('test_span_type', context={}, leaf=False)
        transaction.end_span()
        transaction.begin_span('test_span_type', context={}, leaf=False)
        transaction.end_span()
        transaction.end_transaction()

        transaction_probuf = to_protobuf(transaction.to_dict())

        assert len(transaction_probuf.frame.frames) == 2

    def test_to_protobuf_tree_span(self):
        trace_parent = TraceParent("2.0", "some_id", None)

        transaction = Transaction("request", trace_parent, meta_data=self.client.get_meta_data())
        transaction.begin_span('test_span_type_1', context={}, leaf=False)
        transaction.begin_span('test_span_type_2', context={}, leaf=False)
        transaction.end_span()
        transaction.end_span()
        transaction.end_transaction()

        transaction_probuf = to_protobuf(transaction.to_dict())

        assert len(transaction_probuf.frame.frames) == 1
        assert transaction_probuf.frame.frames[0].call == 'test_span_type_1'
        assert len(transaction_probuf.frame.frames[0].frames) == 1
        assert transaction_probuf.frame.frames[0].frames[0].call == 'test_span_type_2'

    def test_to_probobuf_with_exception(self):
        trace_parent = TraceParent("2.0", "some_id", None)
        transaction = Transaction("request", trace_parent, meta_data=self.client.get_meta_data())
        try:
            1 / 0
        except Exception:
            exc_info = sys.exc_info()
            transaction.add_exception(exception=get_exception_context(exc_info[1], exc_info[2]))

        transaction.end_transaction()

        transaction_probuf = to_protobuf(transaction.to_dict())

        assert transaction_probuf.frame.exceptions
        assert transaction_probuf.frame.exceptions[0].caught_by == 'ToProtobufTest'
        assert transaction_probuf.frame.exceptions[0].exception == 'ZeroDivisionError'
        assert transaction_probuf.frame.exceptions[0].message in ['division by zero', 'integer division or modulo by zero']
        assert transaction_probuf.frame.exceptions[0].timestamp_millis
        assert transaction_probuf.frame.exceptions[0].frames
