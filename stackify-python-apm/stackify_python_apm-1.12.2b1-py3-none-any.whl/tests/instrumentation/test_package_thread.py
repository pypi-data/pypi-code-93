import requests
import threading
import time
from multiprocessing import Process
from requests.models import Response
from unittest import TestCase

try:
    from unittest import mock
except Exception:
    import mock

try:
    import _thread
except Exception:
    import thread as _thread


from stackifyapm.base import Client
from stackifyapm.instrumentation import register
from stackifyapm.instrumentation import control
from stackifyapm.traces import execution_context

CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
}


def do_requests(url):
    return requests.get(url)


def do_something():
    pass


class MyThread(threading.Thread):
    def __init__(self, url=None):
        self.url = url
        threading.Thread.__init__(self)
        self.threadLock = threading.Lock()

    def run(self):
        with self.threadLock:
            return requests.get(self.url)


class ThreadInstrumentationTest(TestCase):

    def set_up(self, request_mock, multiprocessing=False):
        CONFIG["MULTIPROCESSING"] = multiprocessing
        self.client = Client(CONFIG)
        http_response = Response()
        http_response.status_code = 200
        request_mock.return_value = http_response

        register._cls_registers = {
            "stackifyapm.instrumentation.packages.requests.RequestsInstrumentation",
            "stackifyapm.instrumentation.packages.thread.ThreadInstrumentation",
        }
        control.instrument()
        self.client.begin_transaction("Test for begin transaction", client=self.client)

    def tearDown(self):
        control.uninstrument()

    @mock.patch('requests.adapters.HTTPAdapter.build_response')
    def test_should_update_transaction_if_using__thread_module(self, request_mock):
        self.set_up(request_mock)
        _thread.start_new_thread(do_something, ())

        time.sleep(1)
        transaction = execution_context.get_transaction()

        assert transaction.get_has_async_spans()

    @mock.patch('requests.adapters.HTTPAdapter.build_response')
    def test_should_update_transaction_if_using_threading_module(self, request_mock):
        self.set_up(request_mock)
        thread = MyThread('https://www.python.org/')
        thread.start()
        thread.join()

        transaction = execution_context.get_transaction()

        assert transaction.get_has_async_spans()

    @mock.patch('requests.adapters.HTTPAdapter.build_response')
    def test_should_update_transaction_if_using_multiprocessing_module(self, request_mock):
        self.set_up(request_mock)
        p = Process(target=do_requests, args=('https://www.python.org/',))
        p.start()
        p.join()

        transaction = execution_context.get_transaction()
        assert transaction.get_has_async_spans()

    @mock.patch('requests.adapters.HTTPAdapter.build_response')
    def test_should_add_async_span_in_transaction_using_thread_module(self, request_mock):
        self.set_up(request_mock)
        _thread.start_new_thread(do_requests, ('http://www.python.org/',))

        time.sleep(1)

        assert_span()

    @mock.patch('requests.adapters.HTTPAdapter.build_response')
    def test_multiprocessing_config_is_False(self, request_mock):
        self.set_up(request_mock)
        p = Process(target=do_requests, args=('http://www.python.org/',))
        p.start()
        p.join()

        time.sleep(1)

        assert_span(False)

    @mock.patch('requests.adapters.HTTPAdapter.build_response')
    def test_multiprocessing_config_is_True(self, request_mock):
        self.set_up(request_mock, multiprocessing=True)
        p = Process(target=do_requests, args=('http://www.python.org/',))
        p.start()
        p.join()

        time.sleep(1)

        assert_span()


def assert_span(span=True):
    transaction = execution_context.get_transaction()

    if not span:
        assert not transaction.get_spans()
        return

    assert transaction
    assert transaction.get_spans()

    span = transaction.get_spans()[0]
    assert span.is_async

    span_data = span.to_dict()
    assert span_data['reqBegin']
    assert span_data['reqEnd']
    assert span_data['transaction_id']
    assert span_data['call'] == 'ext.http.requests'
    assert span_data['props']
    assert span_data['props']['CATEGORY'] == 'Web External'
    assert span_data['props']['SUBCATEGORY'] == 'Execute'
    assert span_data['props']['COMPONENT_CATEGORY'] == 'Web External'
    assert span_data['props']['COMPONENT_DETAIL'] == 'Execute'
    assert span_data['props']['URL'] == 'http://www.python.org/'
    assert span_data['props']['STATUS'] == '200'
    assert span_data['props']['METHOD'] == 'GET'
    assert span_data['props']['TRACETYPE'] == 'ASYNC'
    assert span_data['props']['THREAD_ID']
