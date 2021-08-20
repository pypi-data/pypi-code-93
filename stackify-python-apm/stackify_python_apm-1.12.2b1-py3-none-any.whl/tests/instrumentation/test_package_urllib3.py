import urllib3
from urllib3.response import HTTPResponse
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.base import Client
from stackifyapm.traces import execution_context
from stackifyapm.instrumentation import register
from stackifyapm.instrumentation import control
from stackifyapm.utils.compat import PY3
from stackifyapm.utils.helper import safe_bytes_to_string

CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
    "PREFIX_ENABLED": True,
}


class FP(object):
    close = True

    def __init__(self, data=""):
        self.data = data

    def isclosed(self):
        return self.close

    def read(self):
        self.close = False
        return self.data

    def close(self):
        self.close = True


class Message(object):
    headers = []

    def items(self):
        return self.headers


class UrlLib3InstrumentationTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.urllib3.Urllib3Instrumentation",
        }

    def setUpSuccess(self):
        self.http_response = HTTPResponse(status=200, msg=Message())
        self.http_response._fp = FP()
        self.setUpContinue()

    def setUpFailed(self):
        self.http_response = HTTPResponse(status=400, msg=Message())
        self.http_response._fp = FP()
        self.setUpContinue()

    def setUpPrefix(self):
        msg = Message()
        if PY3:
            msg.headers = {"X-Foo": "X-Bar"}
        else:
            msg.headers = ["X-Foo: X-Bar"]

        self.http_response = HTTPResponse(status=200, msg=msg)
        self.http_response._fp = FP(data=b"test")
        self.setUpContinue()

    def setUpContinue(self):
        self.request_get = mock.patch('urllib3.connectionpool.HTTPConnectionPool._make_request')
        self.request_mock = self.request_get.start()
        self.request_mock.return_value = self.http_response
        control.instrument(client=self.client)
        self.client.begin_transaction("transaction_test")

    def tearDown(self):
        control.uninstrument(client=self.client)
        self.request_get.stop()

    def test_successful_get_request(self):
        self.setUpSuccess()

        http = urllib3.PoolManager()
        http.request('GET', 'http://www.python.org/')

        self.assert_span(method='GET', status="200")

    def test_unsuccessful_get_request(self):
        self.setUpFailed()

        http = urllib3.PoolManager()
        http.request('GET', 'http://www.python.org/')

        self.assert_span(method='GET', status="400")

    def test_successful_post_request(self):
        self.setUpSuccess()

        http = urllib3.PoolManager()
        http.request('POST', 'http://www.python.org/')

        self.assert_span(method='POST', status="200")

    def test_unsuccessful_post_request(self):
        self.setUpFailed()

        http = urllib3.PoolManager()
        http.request('POST', 'http://www.python.org/')

        self.assert_span(method='POST', status="400")

    def test_prefix_data(self):
        self.setUpPrefix()

        http = urllib3.PoolManager()
        response = http.request(
            'POST',
            'http://www.python.org/',
            body=b"test",
            headers={
                'X-Foo': 'X-Bar',
            },
        )

        assert safe_bytes_to_string(response.read()) == 'test'

        self.assert_span(method='POST', status="200", prefix=True)

    def assert_span(self, method, status, prefix=False):
        transaction = execution_context.get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'ext.http.urllib3'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Web External'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'Web External'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Execute'
        assert span_data['props']['URL'] == 'http://www.python.org/'
        assert span_data['props']['STATUS'] == status
        assert span_data['props']['METHOD'] == method

        if prefix:
            assert span_data['props']['PREFIX_REQUEST_BODY'] == "test"
            assert span_data['props']['PREFIX_REQUEST_SIZE_BYTES'] == "4"
            assert "X-Foo" in span_data['props']['PREFIX_REQUEST_HEADERS']
            assert span_data['props']['PREFIX_RESPONSE_BODY'] == "test"
            assert span_data['props']['PREFIX_RESPONSE_SIZE_BYTES'] == "4"
            assert "X-Foo" in span_data['props']['PREFIX_RESPONSE_HEADERS']
