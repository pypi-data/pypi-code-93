import logging
from unittest import TestCase

from stackifyapm.base import Client
from stackifyapm.traces import execution_context
from stackifyapm.instrumentation import register
from stackifyapm.instrumentation import control
from stackifyapm.utils.compat import PY3

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


class RequestInstrumentationTest(TestCase):
    def set_up(self, prefix_enabled=True):
        CONFIG['PREFIX_ENABLED'] = prefix_enabled

        register._cls_registers = {
            "stackifyapm.instrumentation.packages.logger.LoggerInstrumentation",
        }

        self.client = Client(CONFIG)
        control.instrument(client=self.client)
        self.client.begin_transaction("transaction_test")

    def tearDown(self):
        control.uninstrument(client=self.client)
        self.client.end_transaction()

    def test_prefix_disabled(self):
        self.set_up(prefix_enabled=False)

        logger = logging.getLogger()
        logger.level = logging.INFO
        logger.info('test info logging')

        self.assert_span(level='INFO', message='test info logging', prefix_enabled=False)

    def test_prefix_enabled(self):
        self.set_up(prefix_enabled=True)

        logger = logging.getLogger()
        logger.level = logging.INFO
        logger.info('test info logging')

        self.assert_span(level='INFO', message='test info logging', prefix_enabled=True)

    def test_root_logger(self):
        self.set_up(prefix_enabled=True)

        logger = logging.getLogger()
        logger.level = logging.INFO
        logger.info('test info logging')

        self.assert_span(level='INFO', message='test info logging', prefix_enabled=True)

    def test_named_logger(self):
        self.set_up(prefix_enabled=True)

        logger = logging.getLogger("test_named_logger")
        logger.level = logging.INFO
        logger.info('test info logging')

        self.assert_span(level='INFO', message='test info logging', prefix_enabled=True)

    def test_logging_info(self):
        self.set_up(prefix_enabled=True)

        logger = logging.getLogger()
        logger.level = logging.INFO
        logger.info('test info logging')

        self.assert_span(level='INFO', message='test info logging', prefix_enabled=True)

    def test_logging_warning(self):
        self.set_up(prefix_enabled=True)

        logger = logging.getLogger()
        logger.level = logging.WARNING
        logger.warning('test warning logging')

        self.assert_span(level='WARNING', message='test warning logging', prefix_enabled=True)

    def test_logging_debug(self):
        self.set_up(prefix_enabled=True)

        logger = logging.getLogger()
        logger.level = logging.DEBUG
        logger.debug('test debug logging')

        self.assert_span(level='DEBUG', message='test debug logging', prefix_enabled=True)

    def test_logging_error(self):
        self.set_up(prefix_enabled=True)

        logger = logging.getLogger()
        logger.level = logging.ERROR
        logger.error('test error logging')

        self.assert_span(level='ERROR', message='test error logging', prefix_enabled=True)

    def test_logging_critical(self):
        self.set_up(prefix_enabled=True)

        logger = logging.getLogger()
        logger.level = logging.CRITICAL
        logger.critical('test critical logging')

        self.assert_span(level='CRITICAL', message='test critical logging', prefix_enabled=True)

    def test_logging_exception(self):
        self.set_up(prefix_enabled=True)

        logger = logging.getLogger()
        logger.level = logging.DEBUG
        try:
            5 / 0
        except Exception as e:
            logger.exception(e)

        message = 'division by zero' if PY3 else 'integer division or modulo by zero'
        self.assert_span(level='ERROR', message=message, prefix_enabled=True, exception=True)

    def assert_span(self, level, message, prefix_enabled=False, exception=False):
        transaction = execution_context.get_transaction()
        assert transaction

        if not prefix_enabled:
            assert not transaction.get_spans()
            return
        else:
            assert transaction.get_spans()

        span = transaction.get_spans()[0]
        span_data = span.to_dict()

        assert span_data['reqBegin']
        assert span_data['reqEnd']
        assert span_data['transaction_id']
        assert span_data['call'] == 'cpython.logging'
        assert span_data['props']
        assert span_data['props']['PREFIX'] == 'TRUE'
        assert span_data['props']['CATEGORY'] == 'Log'
        assert span_data['props']['SUBCATEGORY'] == 'Logger'
        assert span_data['props']['LEVEL'] == level
        assert span_data['props']['MESSAGE'] == message

        if exception:
            assert span_data['props']['EXCEPTION']
