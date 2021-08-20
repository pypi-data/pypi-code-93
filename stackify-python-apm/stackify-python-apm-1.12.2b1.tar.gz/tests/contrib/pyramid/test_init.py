import json
import webtest
from pyramid import testing
from pyramid.renderers import render_to_response
from pyramid.response import Response
from pyramid.view import view_config
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.base import Client
from stackifyapm.conf.constants import RUM_COOKIE_NAME
from stackifyapm.contrib.pyramid import make_client
from stackifyapm.instrumentation import control

import base64

CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "Test",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "MyApplication",
    "BASE_DIR": "path/to/application/",
    "RUM_SCRIPT_URL": "https://stckjs.com/test.js",
    "RUM_KEY": "LOREM123"
}


class RegistryMock(object):
    settings = {}

    def __init__(self, name=None, env=None, config_file=None):
        self.settings['APPLICATION_NAME'] = name
        self.settings['ENVIRONMENT'] = env
        self.settings['CONFIG_FILE'] = config_file


class MakeClientTest(TestCase):

    def test_should_return_client(self):
        registry = RegistryMock()
        client = make_client(registry, **registry.settings)

        assert isinstance(client, Client)

    def test_client_default_config(self):
        registry = RegistryMock()
        client = make_client(registry)

        assert client.config.application_name == 'Python Application'
        assert client.config.environment == 'Production'
        assert client.config.config_file == 'stackify.json'
        assert client.config.framework_name == 'pyramid'
        assert client.config.framework_version

    def test_client_config(self):
        registry = RegistryMock(name='MyApp', env='Prod', config_file='somewhere/stackify.json')
        client = make_client(registry)

        assert client.config.application_name == 'MyApp'
        assert client.config.environment == 'Prod'
        assert client.config.config_file == 'somewhere/stackify.json'
        assert client.config.framework_name == 'pyramid'
        assert client.config.framework_version


@view_config(renderer='json')
def index(request):
    return Response(json.dumps({'status': 'OK!'}))


@view_config(renderer='json')
def exception(request):
    5 / 0
    return Response(json.dumps({'status': 'OK!'}))


class Custom(object):
    def __init__(self, request):
        self.request = request

    @view_config(renderer='json')
    def custom_task_one(self):
        return Response(json.dumps({'status': 'OK!'}))

    @view_config(renderer='json')
    def custom_task_two(self):
        return Response(json.dumps({'status': 'OK!'}))


class StackifyPyramidClientTest(TestCase):
    def setUp(self):
        # mock setup logging so it will not log any traces
        self.setup_logging = mock.patch('stackifyapm.conf.setup_logging')
        self.setup_logging.start()

        self.config = testing.setUp(settings={
            'application_name': 'MyApplication',
            'environment': 'Test',
            'rum_enabled': False,
        })
        self.config.add_route('hello', '/')
        self.config.add_route('exception', '/exception')
        self.config.add_route('custom_task_one', '/custom_task_one')
        self.config.add_route('custom_task_two', '/custom_task_two')
        self.config.add_view(index, route_name='hello')
        self.config.add_view(exception, route_name='exception')
        self.config.add_view(Custom, route_name='custom_task_one', attr='custom_task_one')
        self.config.add_view(Custom, route_name='custom_task_two', attr='custom_task_two')
        self.config.include('stackifyapm.contrib.pyramid')
        self.app = None

    def tearDown(self):
        testing.tearDown()
        control.uninstrument()
        self.setup_logging.stop()

    @mock.patch('stackifyapm.base.setup_logging')
    def test_failing_creation_pyramid_apm(self, setup_logging_mock):
        setup_logging_mock.side_effect = Exception("Some Exception")

        # test should not raise Exception
        self.app = webtest.TestApp(self.config.make_wsgi_app())

    @mock.patch('stackifyapm.base.Client.begin_transaction')
    def test_begin_transaction(self, mock_begin_transaction):
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        self.app.get('/')

        assert mock_begin_transaction.called
        assert mock_begin_transaction.call_args_list[0][0][0] == 'request'

    @mock.patch('stackifyapm.base.Client.end_transaction')
    def test_end_transaction(self, mock_end_transaction):
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        self.app.get('/')

        assert mock_end_transaction.called

    @mock.patch('stackifyapm.base.Client.end_transaction')
    @mock.patch('stackifyapm.base.Client.capture_exception')
    def test_capture_exception(self, mock_capture_exception, mock_end_transaction):
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        with self.assertRaises(ZeroDivisionError):
            self.app.get('/exception')

        assert mock_capture_exception.called
        assert mock_capture_exception.call_args_list[0][1]['exception']
        assert mock_capture_exception.call_args_list[0][1]['exception']['Frames']
        assert mock_capture_exception.call_args_list[0][1]['exception']['Timestamp']
        assert mock_capture_exception.call_args_list[0][1]['exception']['Exception']
        assert mock_capture_exception.call_args_list[0][1]['exception']['CaughtBy']
        assert mock_capture_exception.call_args_list[0][1]['exception']['Message']

    @mock.patch('stackifyapm.contrib.pyramid.set_transaction_context')
    def test_reporting_url_custom_task_one(self, mock_set_transaction_context):
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        self.app.get('/custom_task_one')

        assert mock_set_transaction_context.called
        assert mock_set_transaction_context.call_count == 3
        assert mock_set_transaction_context.call_args_list[2][0][0] == 'Custom#custom_task_one'
        assert mock_set_transaction_context.call_args_list[2][0][1] == 'reporting_url'

    @mock.patch('stackifyapm.contrib.pyramid.set_transaction_context')
    def test_reporting_url_custom_task_two(self, mock_set_transaction_context):
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        self.app.get('/custom_task_two')

        assert mock_set_transaction_context.called
        assert mock_set_transaction_context.call_count == 3
        assert mock_set_transaction_context.call_args_list[2][0][0] == 'Custom#custom_task_two'
        assert mock_set_transaction_context.call_args_list[2][0][1] == 'reporting_url'


class StackifyapmHeaderTest(TestCase):
    def setUp(self):
        # mock setup logging so it will not log any traces
        self.setup_logging = mock.patch('stackifyapm.conf.setup_logging')
        self.setup_logging.start()

        self.config = testing.setUp(settings={
            'application_name': 'MyApplication',
            'environment': 'Test',
            'rum_enabled': False,
        })
        self.config.add_route('hello', '/')
        self.config.add_route('exception', '/exception')
        self.config.add_view(index, route_name='hello')
        self.config.add_view(exception, route_name='exception')
        self.config.include('stackifyapm.contrib.pyramid')

    def tearDown(self):
        testing.tearDown()
        control.uninstrument()
        self.setup_logging.stop()

    def test_response_should_contain_stackify_header(self):
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        res = self.app.get('/')

        assert 'X-StackifyID' in res.headers.keys()

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_stackify_header_should_not_include_client_and_device_id(self, get_property_info_mock):
        get_property_info_mock.return_value = {}
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        res = self.app.get('/')

        assert "C" not in res.headers.get('X-StackifyID')
        assert "CD" not in res.headers.get('X-StackifyID')

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_stackify_header_should_contain_client_id(self, get_property_info_mock):
        get_property_info_mock.return_value = {"clientId": "some_id"}
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        res = self.app.get('/')

        assert "Csome_id" in res.headers.get('X-StackifyID')
        assert "CDsome_id" not in res.headers.get('X-StackifyID')

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_stackify_header_should_contain_device_id(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "some_id"}
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        res = self.app.get('/')

        assert "Csome_id" not in res.headers.get('X-StackifyID')
        assert "CDsome_id" in res.headers.get('X-StackifyID')

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_stackify_header_should_contain_client_and_device_id(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "some_id", "clientId": "some_id"}
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        res = self.app.get('/')

        assert "Csome_id" in res.headers.get('X-StackifyID')
        assert "CDsome_id" in res.headers.get('X-StackifyID')

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_get_client_property_call(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "some_id", "clientId": "some_id"}
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        # do multiple requests
        self.app.get('/')
        self.app.get('/')
        res = self.app.get('/')

        assert get_property_info_mock.call_count == 1
        assert "Csome_id" in res.headers.get('X-StackifyID')
        assert "CDsome_id" in res.headers.get('X-StackifyID')

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_get_client_property_call_fallback(self, get_property_info_mock):
        get_property_info_mock.side_effect = [
            {},  # first get_properties call making sure property is empty
            {"deviceId": "some_id", "clientId": "some_id"},  # second get_properties call
        ]
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        # do multiple requests
        self.app.get('/')
        self.app.get('/')
        res = self.app.get('/')

        assert get_property_info_mock.call_count == 2
        assert "Csome_id" in res.headers.get('X-StackifyID')
        assert "CDsome_id" in res.headers.get('X-StackifyID')


def rum_auto_injection(request):
    return render_to_response(
        './fixtures/base.pt',
        {},
        request=request,
    )


class StackifyapmRUMTest(TestCase):
    def setUp(self):
        # mock setup logging so it will not log any traces
        self.setup_logging = mock.patch('stackifyapm.conf.setup_logging')
        self.setup_logging.start()

        self.config = testing.setUp(settings={
            'application_name': 'MyApplication',
            'environment': 'Test',
            'rum_enabled': True,
            'rum_script_url': CONFIG["RUM_SCRIPT_URL"],
            'rum_key': CONFIG["RUM_KEY"]
        })
        self.config.add_route('rum_auto_injection', '/rum_auto')
        self.config.add_view(rum_auto_injection, route_name='rum_auto_injection')
        self.config.add_route('rum_masked_reporting_url', '/rum_masking/192.168.0.1/12/2d64ec54-06ec-4d41-9499-3eb218693a07/test-email.test+01@gmail.com/asd;asd/asdfsdfsdf/{id:.*}')
        self.config.add_view(rum_auto_injection, route_name='rum_masked_reporting_url')
        self.config.include('pyramid_chameleon')
        self.config.include('stackifyapm.contrib.pyramid')

    def tearDown(self):
        testing.tearDown()
        control.uninstrument()
        self.setup_logging.stop()

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_response_should_contain_stackify_rum_cookie(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        res = self.app.get('/rum_auto')
        cookies = [header for header in res.headerlist if header[0] == 'Set-Cookie' and RUM_COOKIE_NAME in header[1]]

        assert not any(cookies)

    @mock.patch('stackifyapm.base.Client.queue')
    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_rum_auto_injection(self, get_property_info_mock, mock_queue):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.app = webtest.TestApp(self.config.make_wsgi_app())
        res = self.app.get('/rum_auto')

        stackify_id = [header for header in res.headerlist if header[0] == 'X-StackifyID'][0][1]
        rum_settings = {
            "ID": "",
            "Name": base64.b64encode(CONFIG["APPLICATION_NAME"].encode("utf-8")).decode("utf-8"),
            "Env": base64.b64encode(CONFIG["ENVIRONMENT"].encode("utf-8")).decode("utf-8"),
            "Trans": base64.b64encode("GET-/rum_auto".encode("utf-8")).decode("utf-8")
        }
        if stackify_id:
            rum_settings["ID"] = stackify_id.split('|')[1]

        result_string = '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="{}" data-key="{}" async></script>'.format(
            json.dumps(rum_settings),
            CONFIG["RUM_SCRIPT_URL"],
            CONFIG["RUM_KEY"]
        )
        assert result_string in str(res.text)
        assert mock_queue.called
        transaction_dict = mock_queue.call_args_list[0][0][0].to_dict()
        assert transaction_dict.get('props', {}).get('ISRUM') == 'TRUE'

    @mock.patch('stackifyapm.base.Client.queue')
    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_rum_trace_property(self, get_property_info_mock, mock_queue):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        res = self.app.get('/rum_auto')
        cookies = [header for header in res.headerlist if header[0] == 'Set-Cookie' and RUM_COOKIE_NAME in header[1]]

        assert not any(cookies)

    @mock.patch('stackifyapm.base.Client.queue')
    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_rum_masked_reporting_url(self, get_property_info_mock, mock_queue):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.app = webtest.TestApp(self.config.make_wsgi_app())
        res = self.app.get('/rum_masking/192.168.0.1/12/2d64ec54-06ec-4d41-9499-3eb218693a07/test-email.test+01@gmail.com/asd;asd/asdfsdfsdf/')

        stackify_id = [header for header in res.headerlist if header[0] == 'X-StackifyID'][0][1]
        rum_settings = {
            "ID": "",
            "Name": base64.b64encode(CONFIG["APPLICATION_NAME"].encode("utf-8")).decode("utf-8"),
            "Env": base64.b64encode(CONFIG["ENVIRONMENT"].encode("utf-8")).decode("utf-8"),
            "Trans": base64.b64encode("GET-/rum_masking/{ip}/{id}/{guid}/{email}/asd/asdfsdfsdf".encode("utf-8")).decode("utf-8")
        }
        if stackify_id:
            rum_settings["ID"] = stackify_id.split('|')[1]

        result_string = '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="{}" data-key="{}" async></script>'.format(
            json.dumps(rum_settings),
            CONFIG["RUM_SCRIPT_URL"],
            CONFIG["RUM_KEY"]
        )
        assert result_string in str(res.text)
        assert mock_queue.called
        transaction_dict = mock_queue.call_args_list[0][0][0].to_dict()
        assert transaction_dict.get('props', {}).get('ISRUM') == 'TRUE'

    @mock.patch('stackifyapm.base.Client.queue')
    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_rum_masked_reporting_url_encoded(self, get_property_info_mock, mock_queue):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.app = webtest.TestApp(self.config.make_wsgi_app())
        res = self.app.get('/rum_masking/192.168.0.1/12/2d64ec54-06ec-4d41-9499-3eb218693a07/test-email.test%2B01%40gmail.com/asd%3Basd/asdfsdfsdf/')

        stackify_id = [header for header in res.headerlist if header[0] == 'X-StackifyID'][0][1]
        rum_settings = {
            "ID": "",
            "Name": base64.b64encode(CONFIG["APPLICATION_NAME"].encode("utf-8")).decode("utf-8"),
            "Env": base64.b64encode(CONFIG["ENVIRONMENT"].encode("utf-8")).decode("utf-8"),
            "Trans": base64.b64encode("GET-/rum_masking/{ip}/{id}/{guid}/{email}/asd/asdfsdfsdf".encode("utf-8")).decode("utf-8")
        }
        if stackify_id:
            rum_settings["ID"] = stackify_id.split('|')[1]

        result_string = '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="{}" data-key="{}" async></script>'.format(
            json.dumps(rum_settings),
            CONFIG["RUM_SCRIPT_URL"],
            CONFIG["RUM_KEY"]
        )
        assert result_string in str(res.text)
        assert mock_queue.called
        transaction_dict = mock_queue.call_args_list[0][0][0].to_dict()
        assert transaction_dict.get('props', {}).get('ISRUM') == 'TRUE'


class TestPrefixInstrumentation(TestCase):
    def setUp(self):
        # mock setup logging so it will not log any traces
        self.setup_logging = mock.patch('stackifyapm.conf.setup_logging')
        self.setup_logging.start()

        self.config = testing.setUp(settings={
            'application_name': 'MyApplication',
            'environment': 'Test',
            'prefix_enabled': True,
            'rum_enabled': False,
        })
        self.config.add_route('hello', '/')
        self.config.add_route('exception', '/exception')
        self.config.add_view(index, route_name='hello')
        self.config.add_view(exception, route_name='exception')
        self.config.include('stackifyapm.contrib.pyramid')

    def tearDown(self):
        testing.tearDown()
        control.uninstrument()
        self.setup_logging.stop()

    @mock.patch('stackifyapm.base.Client.queue')
    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_prefix_data(self, get_property_info_mock, queue_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        self.app.post('/', json.dumps({"foo": "bar"}), headers={"Content-Type": "x-test"})

        assert queue_mock.called
        transaction_dict = queue_mock.call_args_list[0][0][0].to_dict()

        assert transaction_dict.get('props', {}).get('PREFIX_REQUEST_BODY')
        assert transaction_dict.get('props', {}).get('PREFIX_REQUEST_SIZE_BYTES')
        assert transaction_dict.get('props', {}).get('PREFIX_REQUEST_HEADERS')
        assert transaction_dict.get('props', {}).get('PREFIX_RESPONSE_BODY')
        assert transaction_dict.get('props', {}).get('PREFIX_RESPONSE_SIZE_BYTES')
        assert transaction_dict.get('props', {}).get('PREFIX_RESPONSE_HEADERS')

    @mock.patch('stackifyapm.base.Client.queue')
    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_prefix_data_with_exception(self, get_property_info_mock, queue_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.app = webtest.TestApp(self.config.make_wsgi_app())

        with self.assertRaises(Exception):
            self.app.post('/exception', json.dumps({"foo": "bar"}), headers={"Content-Type": "x-test"})

        assert queue_mock.called
        transaction_dict = queue_mock.call_args_list[0][0][0].to_dict()

        assert transaction_dict.get('props', {}).get('PREFIX_REQUEST_BODY')
        assert transaction_dict.get('props', {}).get('PREFIX_REQUEST_SIZE_BYTES')
        assert transaction_dict.get('props', {}).get('PREFIX_REQUEST_HEADERS')
        assert not transaction_dict.get('props', {}).get('PREFIX_RESPONSE_BODY')
        assert not transaction_dict.get('props', {}).get('PREFIX_RESPONSE_SIZE_BYTES')
        assert not transaction_dict.get('props', {}).get('PREFIX_RESPONSE_HEADERS')
