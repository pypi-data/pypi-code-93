import imp
import requests
from requests.models import Response
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.contrib.azure_function import instrument
from stackifyapm.contrib.azure_function import StackifyAPM
from stackifyapm.instrumentation import register
from stackifyapm.instrumentation import control


CONFIG = {
    'application_name': 'sample_azure',
    'environment': 'test',
}


class MockContext(object):
    function_name = 'sample_name'


class AzureFunctionManualIntegrationTest(TestCase):
    def setUp(self):
        # mock setup logging so it will not log any traces
        self.setup_logging = mock.patch('stackifyapm.conf.setup_logging')
        self.setup_logging.start()
        register._cls_registers = {
            'stackifyapm.instrumentation.packages.requests.RequestsInstrumentation',
        }

    def tearDown(self):
        control.uninstrument()
        self.setup_logging.stop()

    @mock.patch('stackifyapm.base.Client.queue')
    def test_azure_function(self, mock_queue):
        req = object()

        @StackifyAPM(**CONFIG)
        def sample_azure_function(req):
            pass

        sample_azure_function(req)

        assert mock_queue.called

        transaction_dict = mock_queue.call_args_list[0][0][0].to_dict()

        assert transaction_dict['call'] == 'sample_azure_function'
        assert transaction_dict['props']['REPORTING_URL'] == 'sample_azure_function'
        assert transaction_dict['props']['APPLICATION_NAME'] == 'sample_azure'
        assert transaction_dict['props']['APPLICATION_ENV'] == 'test'
        assert transaction_dict['props']['TRACETYPE'] == 'TASK'

    @mock.patch('stackifyapm.base.Client.queue')
    @mock.patch('requests.adapters.HTTPAdapter.build_response')
    def test_azure_function_with_instrument(self, mock_request, mock_queue):
        mock_request.return_value = Response()
        mock_request.return_value.status_code = 200
        req = object()
        instrument()

        @StackifyAPM(**CONFIG)
        def sample_azure_function(req):
            return requests.get('https://www.python.org/')

        sample_azure_function(req)

        assert mock_queue.called
        assert mock_request.called

        transaction_dict = mock_queue.call_args_list[0][0][0].to_dict()

        assert transaction_dict['call'] == 'sample_azure_function'
        assert transaction_dict['props']['REPORTING_URL'] == 'sample_azure_function'
        assert transaction_dict['props']['APPLICATION_NAME'] == 'sample_azure'
        assert transaction_dict['props']['APPLICATION_ENV'] == 'test'
        assert transaction_dict['props']['TRACETYPE'] == 'TASK'
        assert transaction_dict['stacks']
        assert transaction_dict['stacks'][0]['call'] == 'ext.http.requests'
        assert transaction_dict['stacks'][0]['props']['URL'] == 'https://www.python.org/'
        assert transaction_dict['stacks'][0]['props']['METHOD'] == 'GET'
        assert transaction_dict['stacks'][0]['props']['STATUS'] == '200'

    @mock.patch('stackifyapm.base.Client.queue')
    def test_azure_function_with_exception(self, mock_queue):
        req = object()

        @StackifyAPM(**CONFIG)
        def sample_azure_function(req):
            raise Exception('test_error')

        with self.assertRaises(Exception):
            sample_azure_function(req)

        assert mock_queue.called

        transaction_dict = mock_queue.call_args_list[0][0][0].to_dict()

        assert transaction_dict['call'] == 'sample_azure_function'
        assert transaction_dict['props']['REPORTING_URL'] == 'sample_azure_function'
        assert transaction_dict['props']['APPLICATION_NAME'] == 'sample_azure'
        assert transaction_dict['props']['APPLICATION_ENV'] == 'test'
        assert transaction_dict['props']['TRACETYPE'] == 'TASK'
        assert transaction_dict['exceptions']
        assert transaction_dict['exceptions'][0]['Message'] == 'test_error'


class AzureFunctionAutoIntegrationTest(TestCase):
    def setUp(self):
        # mock setup logging so it will not log any traces
        self.setup_logging = mock.patch('stackifyapm.conf.setup_logging')
        self.setup_logging.start()
        register._cls_registers = {
            'stackifyapm.instrumentation.packages.requests.RequestsInstrumentation',
        }

    def tearDown(self):
        control.uninstrument()
        self.setup_logging.stop()

    @mock.patch('stackifyapm.base.Client.queue')
    def test_simple_handler_function(self, mock_queue):
        req = object()

        from tests.contrib.azure_function import fixtures
        imp.reload(fixtures)
        fixtures.test_azure_function(req)

        assert mock_queue.called

        transaction_dict = mock_queue.call_args_list[0][0][0].to_dict()

        assert transaction_dict['call'] == 'test_azure_function'
        assert transaction_dict['props']['REPORTING_URL'] == 'test_azure_function'
        assert transaction_dict['props']['APPLICATION_NAME'] == 'Python Application'
        assert transaction_dict['props']['APPLICATION_ENV'] == 'Production'
        assert transaction_dict['props']['TRACETYPE'] == 'TASK'

    @mock.patch('stackifyapm.base.Client.queue')
    def test_azure_function(self, mock_queue):
        req = object()
        context = MockContext()

        from tests.contrib.azure_function import fixtures
        imp.reload(fixtures)
        fixtures.test_azure_function_with_context(req, context=context)

        assert mock_queue.called

        transaction_dict = mock_queue.call_args_list[0][0][0].to_dict()

        assert transaction_dict['call'] == 'sample_name'
        assert transaction_dict['props']['REPORTING_URL'] == 'sample_name'
        assert transaction_dict['props']['APPLICATION_NAME'] == 'Python Application'
        assert transaction_dict['props']['APPLICATION_ENV'] == 'Production'
        assert transaction_dict['props']['TRACETYPE'] == 'TASK'

    @mock.patch('stackifyapm.base.Client.queue')
    @mock.patch('requests.adapters.HTTPAdapter.build_response')
    def test_azure_function_with_instrument(self, mock_request, mock_queue):

        mock_request.return_value = Response()
        mock_request.return_value.status_code = 200
        req = object()

        from tests.contrib.azure_function import fixtures
        imp.reload(fixtures)
        fixtures.test_azure_function_with_span(req)

        assert mock_queue.called
        assert mock_request.called

        transaction_dict = mock_queue.call_args_list[0][0][0].to_dict()

        assert transaction_dict['call'] == 'test_azure_function_with_span'
        assert transaction_dict['props']['REPORTING_URL'] == 'test_azure_function_with_span'
        assert transaction_dict['props']['APPLICATION_NAME'] == 'Python Application'
        assert transaction_dict['props']['APPLICATION_ENV'] == 'Production'
        assert transaction_dict['props']['TRACETYPE'] == 'TASK'
        assert transaction_dict['stacks']
        assert transaction_dict['stacks'][0]['call'] == 'ext.http.requests'
        assert transaction_dict['stacks'][0]['props']['URL'] == 'https://www.python.org/'
        assert transaction_dict['stacks'][0]['props']['METHOD'] == 'GET'
        assert transaction_dict['stacks'][0]['props']['STATUS'] == '200'

    @mock.patch('stackifyapm.base.Client.queue')
    def test_azure_function_with_exception(self, mock_queue):
        req = object()

        from tests.contrib.azure_function import fixtures
        imp.reload(fixtures)

        with self.assertRaises(Exception):
            fixtures.test_azure_function_with_exception(req)

        assert mock_queue.called

        transaction_dict = mock_queue.call_args_list[0][0][0].to_dict()

        assert transaction_dict['call'] == 'test_azure_function_with_exception'
        assert transaction_dict['props']['REPORTING_URL'] == 'test_azure_function_with_exception'
        assert transaction_dict['props']['APPLICATION_NAME'] == 'Python Application'
        assert transaction_dict['props']['APPLICATION_ENV'] == 'Production'
        assert transaction_dict['props']['TRACETYPE'] == 'TASK'
        assert transaction_dict['exceptions']
        assert transaction_dict['exceptions'][0]['Message'] == 'test_error'

    @mock.patch('stackifyapm.base.Client.queue')
    def test_azure_function_with_options(self, mock_queue):
        req = object()

        from tests.contrib.azure_function import fixtures
        imp.reload(fixtures)
        fixtures.test_azure_function_with_options(req)

        assert mock_queue.called

        transaction_dict = mock_queue.call_args_list[0][0][0].to_dict()

        assert transaction_dict['call'] == 'test_azure_function_with_options'
        assert transaction_dict['props']['REPORTING_URL'] == 'test_azure_function_with_options'
        assert transaction_dict['props']['APPLICATION_NAME'] == 'test_name'
        assert transaction_dict['props']['APPLICATION_ENV'] == 'test'
        assert transaction_dict['props']['TRACETYPE'] == 'TASK'
