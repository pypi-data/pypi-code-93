import imp
import os
import requests
from requests.models import Response
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.contrib.aws_lambda import instrument
from stackifyapm.contrib.aws_lambda import StackifyAPM
from stackifyapm.instrumentation import register
from stackifyapm.instrumentation import control


CONFIG = {
    'application_name': 'sample_lambda',
    'environment': 'production',
}


class MockContext(object):
    function_name = 'sample_name'
    invoked_function_arn = 'sample_arn'


class AWSLambdaManualIntegrationTest(TestCase):
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
    def test_lambda(self, mock_queue):
        event = object()
        context = MockContext()

        @StackifyAPM(**CONFIG)
        def sample_lambda_handler(event, context):
            return True

        sample_lambda_handler(event, context)

        assert mock_queue.called

        transaction_dict = mock_queue.call_args_list[0][0][0].to_dict()

        assert transaction_dict['call'] == 'sample_name'
        assert transaction_dict['props']['REPORTING_URL'] == 'sample_name'
        assert transaction_dict['props']['APPLICATION_NAME'] == 'sample_lambda'
        assert transaction_dict['props']['APPLICATION_ENV'] == 'production'
        assert transaction_dict['props']['TRACETYPE'] == 'TASK'
        assert transaction_dict['props']['AWS_LAMBDA_ARN'] == 'sample_arn'

    @mock.patch('stackifyapm.base.Client.queue')
    @mock.patch('requests.adapters.HTTPAdapter.build_response')
    def test_lambda_with_instrument(self, mock_request, mock_queue):
        mock_request.return_value = Response()
        mock_request.return_value.status_code = 200
        event = object()
        context = MockContext()
        instrument()

        @StackifyAPM(**CONFIG)
        def sample_lambda_handler(event, context):
            requests.get('https://www.python.org/')

        sample_lambda_handler(event, context)

        assert mock_queue.called
        assert mock_request.called

        transaction_dict = mock_queue.call_args_list[0][0][0].to_dict()

        assert transaction_dict['call'] == 'sample_name'
        assert transaction_dict['props']['REPORTING_URL'] == 'sample_name'
        assert transaction_dict['props']['APPLICATION_NAME'] == 'sample_lambda'
        assert transaction_dict['props']['APPLICATION_ENV'] == 'production'
        assert transaction_dict['props']['TRACETYPE'] == 'TASK'
        assert transaction_dict['props']['AWS_LAMBDA_ARN'] == 'sample_arn'
        assert transaction_dict['stacks']
        assert transaction_dict['stacks'][0]['call'] == 'ext.http.requests'
        assert transaction_dict['stacks'][0]['props']['URL'] == 'https://www.python.org/'
        assert transaction_dict['stacks'][0]['props']['METHOD'] == 'GET'
        assert transaction_dict['stacks'][0]['props']['STATUS'] == '200'

    @mock.patch('stackifyapm.base.Client.queue')
    def test_lambda_with_exception(self, mock_queue):
        event = object()
        context = MockContext()

        @StackifyAPM(**CONFIG)
        def sample_lambda_handler(event, context):
            raise Exception('test_error')

        with self.assertRaises(Exception):
            sample_lambda_handler(event, context)

        assert mock_queue.called

        transaction_dict = mock_queue.call_args_list[0][0][0].to_dict()

        assert transaction_dict['call'] == 'sample_name'
        assert transaction_dict['props']['REPORTING_URL'] == 'sample_name'
        assert transaction_dict['props']['APPLICATION_NAME'] == 'sample_lambda'
        assert transaction_dict['props']['APPLICATION_ENV'] == 'production'
        assert transaction_dict['props']['TRACETYPE'] == 'TASK'
        assert transaction_dict['props']['AWS_LAMBDA_ARN'] == 'sample_arn'
        assert transaction_dict['exceptions']
        assert transaction_dict['exceptions'][0]['Message'] == 'test_error'


class AWSLambdaAutoIntegrationTest(TestCase):
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

    def test_empty_handler(self):
        os.environ["STACKIFY_LAMBDA_HANDLER"] = ""
        del os.environ["STACKIFY_LAMBDA_HANDLER"]
        event = object()
        context = MockContext()

        from stackifyapm.contrib.aws_lambda import function
        imp.reload(function)

        with self.assertRaises(Exception):
            function.handler(event, context)

    @mock.patch('stackifyapm.base.Client.queue')
    def test_lambda(self, mock_queue):
        os.environ["STACKIFY_LAMBDA_HANDLER"] = "tests.contrib.aws_lambda.fixtures.test_handler_function"

        event = object()
        context = MockContext()

        from stackifyapm.contrib.aws_lambda import function
        imp.reload(function)
        function.handler(event, context)

        assert mock_queue.called

        transaction_dict = mock_queue.call_args_list[0][0][0].to_dict()

        assert transaction_dict['call'] == 'sample_name'
        assert transaction_dict['props']['REPORTING_URL'] == 'sample_name'
        assert transaction_dict['props']['APPLICATION_NAME'] == 'Python Application'
        assert transaction_dict['props']['APPLICATION_ENV'] == 'Production'
        assert transaction_dict['props']['TRACETYPE'] == 'TASK'
        assert transaction_dict['props']['AWS_LAMBDA_ARN'] == 'sample_arn'

        del os.environ["STACKIFY_LAMBDA_HANDLER"]

    @mock.patch('stackifyapm.base.Client.queue')
    @mock.patch('requests.adapters.HTTPAdapter.build_response')
    def test_lambda_with_instrument(self, mock_request, mock_queue):
        os.environ["STACKIFY_LAMBDA_HANDLER"] = "tests.contrib.aws_lambda.fixtures.test_handler_function_with_span"

        mock_request.return_value = Response()
        mock_request.return_value.status_code = 200
        event = object()
        context = MockContext()

        from stackifyapm.contrib.aws_lambda import function
        imp.reload(function)
        function.handler(event, context)

        assert mock_queue.called
        assert mock_request.called

        transaction_dict = mock_queue.call_args_list[0][0][0].to_dict()

        assert transaction_dict['call'] == 'sample_name'
        assert transaction_dict['props']['REPORTING_URL'] == 'sample_name'
        assert transaction_dict['props']['APPLICATION_NAME'] == 'Python Application'
        assert transaction_dict['props']['APPLICATION_ENV'] == 'Production'
        assert transaction_dict['props']['TRACETYPE'] == 'TASK'
        assert transaction_dict['props']['AWS_LAMBDA_ARN'] == 'sample_arn'
        assert transaction_dict['stacks']
        assert transaction_dict['stacks'][0]['call'] == 'ext.http.requests'
        assert transaction_dict['stacks'][0]['props']['URL'] == 'https://www.python.org/'
        assert transaction_dict['stacks'][0]['props']['METHOD'] == 'GET'
        assert transaction_dict['stacks'][0]['props']['STATUS'] == '200'

        del os.environ["STACKIFY_LAMBDA_HANDLER"]

    @mock.patch('stackifyapm.base.Client.queue')
    def test_lambda_with_exception(self, mock_queue):
        os.environ["STACKIFY_LAMBDA_HANDLER"] = "tests.contrib.aws_lambda.fixtures.test_handler_function_with_exception"

        event = object()
        context = MockContext()

        from stackifyapm.contrib.aws_lambda import function
        imp.reload(function)

        with self.assertRaises(Exception):
            function.handler(event, context)

        assert mock_queue.called

        transaction_dict = mock_queue.call_args_list[0][0][0].to_dict()

        assert transaction_dict['call'] == 'sample_name'
        assert transaction_dict['props']['REPORTING_URL'] == 'sample_name'
        assert transaction_dict['props']['APPLICATION_NAME'] == 'Python Application'
        assert transaction_dict['props']['APPLICATION_ENV'] == 'Production'
        assert transaction_dict['props']['TRACETYPE'] == 'TASK'
        assert transaction_dict['props']['AWS_LAMBDA_ARN'] == 'sample_arn'
        assert transaction_dict['exceptions']
        assert transaction_dict['exceptions'][0]['Message'] == 'test_error'

        del os.environ["STACKIFY_LAMBDA_HANDLER"]
