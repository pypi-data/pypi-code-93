import urllib
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


class MockFp(object):
    def read(self):
        return b'test'

    def readline(self):
        self.read()


class UrllibInstrumentationTest(TestCase):
    def setUp(self):
        self.client = Client(CONFIG)
        register._cls_registers = {
            "stackifyapm.instrumentation.packages.urllib.UrllibInstrumentation",
        }
        if PY3:
            self.response = mock.patch('http.client.HTTPConnection.getresponse')
        else:
            self.response = mock.patch('httplib.HTTPConnection.getresponse')

    def setUpSuccess(self):
        self.response_mock = self.response.start()
        self.response_mock.return_value = mock.Mock(code=200, status=200, headers={}, msg={})
        self.setUpContinue()

    def setUpFailed(self):
        self.response_mock = self.response.start()
        self.response_mock.return_value = mock.Mock(code=404, status=404, headers={}, reason="", msg={})
        self.setUpContinue()

    def setUpPrefix(self):
        fp = MockFp()
        self.response_mock = self.response.start()
        self.response_mock.return_value = mock.Mock(code=200, status=200, headers={"X-Foo": "X-Bar"}, msg={"X-Foo": "X-Bar"}, fp=fp, read=lambda: 'test')
        self.setUpContinue()

    def setUpContinue(self):
        if PY3:
            self.openurl = mock.patch('http.client.HTTPConnection.request')
            self.openurl_mock = self.openurl.start()
        else:
            self.openurl = mock.patch('urllib.URLopener.open_http')
            self.openurl_mock = self.openurl.start()
            self.openurl_mock.return_value = self.response_mock.return_value

    def tearDown(self):
        control.uninstrument(client=self.client)
        self.openurl and self.openurl_mock.stop()
        self.response_mock.stop()

    def test_successful_request(self):
        self.setUpSuccess()
        control.instrument(client=self.client)
        self.client.begin_transaction("transaction_test")

        if PY3:
            urllib.request.urlopen('http://www.python.org/')
        else:
            urllib.urlopen('http://www.python.org/')

        self.assert_span(status="200")

    def test_unsuccessful_request(self):
        self.setUpFailed()
        control.instrument(client=self.client)
        self.client.begin_transaction("transaction_test")

        if PY3:
            with self.assertRaises(Exception):
                urllib.request.urlopen('http://www.python.org/')
        else:
            urllib.urlopen('http://www.python.org/')

        self.assert_span(status="404")

    def test_prefix_data(self):
        self.setUpPrefix()
        control.instrument(client=self.client)
        self.client.begin_transaction("transaction_test")

        if PY3:
            req = urllib.request.Request('http://www.python.org/', b"test")
            req.add_header('X-foo', 'X-bar')
            response = urllib.request.urlopen(req)
        else:
            response = urllib.urlopen('http://www.python.org/')

        assert safe_bytes_to_string(response.read()) == 'test'

        self.assert_span(status="200", prefix=True)

    def assert_span(self, status, prefix=False):
        if self.openurl:
            assert self.openurl_mock.called

        transaction = execution_context.get_transaction()
        assert transaction
        assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'ext.http.urllib'
        assert span_data['props']
        assert span_data['props']['CATEGORY'] == 'Web External'
        assert span_data['props']['SUBCATEGORY'] == 'Execute'
        assert span_data['props']['COMPONENT_CATEGORY'] == 'Web External'
        assert span_data['props']['COMPONENT_DETAIL'] == 'Execute'
        assert span_data['props']['URL'] == 'http://www.python.org/'
        assert span_data['props']['STATUS'] == status

        if prefix:
            assert span_data['props']['PREFIX_REQUEST_BODY'] == ("test" if PY3 else "")
            assert span_data['props']['PREFIX_REQUEST_SIZE_BYTES'] == ("4" if PY3 else "0")
            if PY3:
                assert "X-foo" in span_data['props']['PREFIX_REQUEST_HEADERS']
            else:
                assert span_data['props']['PREFIX_REQUEST_HEADERS']
            assert span_data['props']['PREFIX_RESPONSE_BODY'] == ""
            assert span_data['props']['PREFIX_RESPONSE_SIZE_BYTES'] == "0"
            assert "X-Foo" in span_data['props']['PREFIX_RESPONSE_HEADERS']
