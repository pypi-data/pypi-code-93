import logging
import os
import re
from stat import ST_MODE
from unittest import SkipTest
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.base import Client
from stackifyapm.conf import Config
from stackifyapm.conf import ConfigError
from stackifyapm.conf import IncrementalFileHandler
from stackifyapm.conf import RegexValidator
from stackifyapm.conf import setup_stackifyapm_logging
from stackifyapm.conf import StackifyFormatter
from stackifyapm.conf.constants import LOG_PATH
from stackifyapm.conf.constants import PREFIX_LOG_PATH


CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
    "ASYNC_MODE": False,
    "CONFIG_FILE": 'path/to/stackify.json',
    "QUEUE": False,
    "PREFIX_ENABLED": True,
    "RUMV2_ENABLED": True,
    "RUM_SCRIPT_URL": "https://stckjs.com/test.js",
    "RUM_KEY": "LOREM123"
}


class RegexValidatorTest(TestCase):

    def test_should_return_correct_value(self):
        regex = "^[a-zA-Z0-9 _-]+$"
        value = 'some_value'
        _validate = RegexValidator(regex)

        validated_value = _validate(value, 'SOME_KEY')

        assert validated_value == value

    def test_should_raise_exception(self):
        regex = "^[a-zA-Z0-9 _-]+$"
        value = '#$%^'
        _validate = RegexValidator(regex)

        with self.assertRaises(ConfigError) as context:
            _validate(value, 'SOME_KEY')

        assert 'does not match pattern' in context.exception.args[0]


class ConfigTest(TestCase):

    def test_config_creation(sself):
        config = Config(CONFIG)

        assert config.environment == CONFIG["ENVIRONMENT"]
        assert config.hostname == CONFIG["HOSTNAME"]
        assert config.framework_name == CONFIG["FRAMEWORK_NAME"]
        assert config.framework_version == CONFIG["FRAMEWORK_VERSION"]
        assert config.application_name == CONFIG["APPLICATION_NAME"]
        assert config.config_file == CONFIG["CONFIG_FILE"]
        assert config.base_dir == CONFIG["BASE_DIR"]
        assert config.async_mode is False
        assert config.queue is False
        assert config.prefix_enabled is True
        assert config.rum_enabled is True
        assert config.rum_script_url == CONFIG["RUM_SCRIPT_URL"]
        assert config.rum_key == CONFIG["RUM_KEY"]

    def test_default_config(self):
        config = Config()

        assert config.application_name == 'Python Application'
        assert config.environment == 'Production'
        assert config.config_file == 'stackify.json'
        assert config.framework_name == ''
        assert config.framework_version == ''
        assert config.base_dir is None
        assert config.async_mode is True
        assert config.queue is True
        assert config.prefix_enabled is False
        assert config.rum_enabled is False
        assert config.rum_script_url == 'https://stckjs.stackify.com/stckjs.js'
        assert config.rum_key == ''

    def test_environment_variables(self):
        os.environ["STACKIFY_TRANSPORT"] = 'agent_socket'
        os.environ["STACKIFY_TRANSPORT_HTTP_ENDPOINT"] = 'http://domain.test'

        config = Config(CONFIG)

        assert config.transport == 'agent_socket'
        assert config.http_endpoint == 'http://domain.test'

        del os.environ["STACKIFY_TRANSPORT"]
        del os.environ["STACKIFY_TRANSPORT_HTTP_ENDPOINT"]


class IncrementalFileHandlerTest(TestCase):

    def setUp(self):
        self.filename = 'somefile.log'
        self.filename1 = self.filename + '.1'

        self.remove_file(self.filename)
        self.remove_file(self.filename1)

    def tearDown(self):
        self.remove_file(self.filename)
        self.remove_file(self.filename1)

    def remove_file(self, filename):
        try:
            os.path.exists(filename) and os.remove(filename)
        except Exception:
            pass

    def test_file_should_be_created(self):
        IncrementalFileHandler(self.filename, maxBytes=100)

        assert os.path.exists(self.filename)
        assert os.path.getsize(self.filename) == 0

    def test_should_log(self):
        logger = logging.getLogger('test')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(IncrementalFileHandler(self.filename, maxBytes=100))

        logger.debug('some data to log')

        assert not os.path.getsize(self.filename) == 0

    def test_should_rotate(self):
        logger = logging.getLogger('test')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(IncrementalFileHandler(self.filename, maxBytes=20))

        logger.debug('some data to log')  # size 17
        logger.debug('some data to log')  # size will go over 20 bytes and will create new file .1

        assert os.path.exists(self.filename)
        assert os.path.exists(self.filename1)

    def test_should_recreate_log_file_if_deleted(self):
        logger = logging.getLogger('test')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(IncrementalFileHandler(self.filename, maxBytes=100))

        # making sure the log file was created
        logger.debug('some data to log')
        assert os.path.exists(self.filename)

        # we cant delete file if still in use
        if not os.name == 'nt':
            # making sure the log file was delete
            self.remove_file(self.filename)
            assert not os.path.exists(self.filename)

        logger.debug('some data to log')
        assert os.path.exists(self.filename)


class SetupLoggingTest(TestCase):
    def setup_check(self, log_path):
        if not os.path.exists(log_path):
            raise SkipTest("Skipping due to LOG_PATH doesn't exists")

    def test_log_file_should_be_created(self):
        CONFIG["PREFIX_ENABLED"] = False
        self.setup_check(LOG_PATH)
        client = Client(CONFIG)
        host_name = client.get_system_info().get("hostname")
        process_id = client.get_process_info().get("pid")
        filename = "{}{}#{}-1.log".format(LOG_PATH, host_name, process_id)

        setup_stackifyapm_logging(client)

        assert os.path.exists(filename)

        try:
            os.path.exists(filename) and os.remove(filename)
        except Exception:
            # we cant delete file in use on windows machine
            pass

    def test_should_log_777_permission(self):
        CONFIG["PREFIX_ENABLED"] = False
        self.setup_check(LOG_PATH)
        client = Client(CONFIG)
        host_name = client.get_system_info().get("hostname")
        process_id = client.get_process_info().get("pid")
        filename = "{}{}#{}-1.log".format(LOG_PATH, host_name, process_id)

        setup_stackifyapm_logging(client)

        assert oct(os.stat(filename)[ST_MODE])[-3:] == '777'

    def test_if_file_remove_log_777_permission_(self):
        CONFIG["PREFIX_ENABLED"] = False
        self.setup_check(LOG_PATH)
        client = Client(CONFIG)
        host_name = client.get_system_info().get("hostname")
        process_id = client.get_process_info().get("pid")
        filename = "{}{}#{}-1.log".format(LOG_PATH, host_name, process_id)

        logger = setup_stackifyapm_logging(client)

        assert os.path.exists(filename)

        try:
            os.remove(filename)
        except Exception:
            # we cant delete file in use on windows machine
            pass

        logger.debug("Test")
        assert oct(os.stat(filename)[ST_MODE])[-3:] == '777'

    def test_log_timestamp_format(self):
        CONFIG["PREFIX_ENABLED"] = False
        self.setup_check(LOG_PATH)
        client = Client(CONFIG)
        host_name = client.get_system_info().get("hostname")
        process_id = client.get_process_info().get("pid")
        filename = "{}{}#{}-1.log".format(LOG_PATH, host_name, process_id)

        logger = setup_stackifyapm_logging(client)

        assert os.path.exists(filename)

        logger.debug("Test")

        file = open(filename, "r")
        log_line = file.read()
        assert re.findall("\\d{4}-\\d{2}-\\d{2}, \\d{2}:\\d{2}:\\d{2}.\\d{6}> ", log_line)

    def test_log_file_should_be_created_on_prefix(self):
        CONFIG["PREFIX_ENABLED"] = True
        self.setup_check(PREFIX_LOG_PATH)
        client = Client(CONFIG)
        host_name = client.get_system_info().get("hostname")
        process_id = client.get_process_info().get("pid")
        filename = "{}{}#{}-1.log".format(PREFIX_LOG_PATH, host_name, process_id)

        setup_stackifyapm_logging(client)

        assert os.path.exists(filename)

        try:
            os.path.exists(filename) and os.remove(filename)
        except Exception:
            # we cant delete file in use on windows machine
            pass

    @mock.patch('stackifyapm.base.Client.get_process_info')
    def test_old_log_files_should_be_deleted(self, get_process_info_mock):
        self.setup_check(PREFIX_LOG_PATH)
        CONFIG["PREFIX_ENABLED"] = False
        get_process_info_mock.side_effect = [{'pid': i} for i in range(16)]
        client = Client(CONFIG)
        host_name = client.get_system_info().get("hostname")

        for _ in range(15):
            setup_stackifyapm_logging(client)

        try:
            filename = "{}{}#{}-1.log".format(LOG_PATH, host_name, 0)
            dir_name = os.path.dirname(filename)
            log_files = sorted([
                os.path.join(dir_name, file)
                for file in os.listdir(dir_name)
                if file.endswith('.log')
            ], key=lambda f: os.stat(f).st_mtime)[::-1]

            assert len(log_files) == 10
        except Exception:
            raise SkipTest('Skipping due to error when getting old log files')


class StackifyMsecFormatTest(TestCase):

    def test_should_msec_format(self):
        record = logging.makeLogRecord({'mgs': 'message'})
        datefmt = '%Y-%m-%d, %H:%M:%S.%f'
        stackify_formatter = StackifyFormatter()

        time_format = stackify_formatter.formatTime(record, datefmt)

        assert re.findall("\\d{4}-\\d{2}-\\d{2}, \\d{2}:\\d{2}:\\d{2}.\\d{6}", time_format)


class EnvironmentVariableTests(TestCase):
    def test_application_name(self):
        os.environ["STACKIFY_APPLICATION_NAME"] = 'test_name'

        config = Config()

        assert config.application_name == 'test_name'

        del os.environ["STACKIFY_APPLICATION_NAME"]

    def test_environment(self):
        os.environ["STACKIFY_ENVIRONMENT_NAME"] = 'test_environment'

        config = Config()

        assert config.environment == 'test_environment'

        del os.environ["STACKIFY_ENVIRONMENT_NAME"]

    def test_config_file(self):
        os.environ["STACKIFY_CONFIG_FILE"] = 'test_config_file'

        config = Config()

        assert config.config_file == 'test_config_file'

        del os.environ["STACKIFY_CONFIG_FILE"]

    def test_multiprocessing(self):
        os.environ["STACKIFY_MULTIPROCESSING"] = 'True'

        config = Config()

        assert config.multiprocessing is True

        del os.environ["STACKIFY_MULTIPROCESSING"]

    def test_rum_enabled(self):
        os.environ["RETRACE_RUMV2_ENABLED"] = 'True'

        config = Config()

        assert config.rum_enabled is True

        del os.environ["RETRACE_RUMV2_ENABLED"]

    def test_rum_script_url_valid(self):
        os.environ["RETRACE_RUM_SCRIPT_URL"] = 'https://test.com/test.js'

        config = Config()

        assert config.rum_script_url == 'https://test.com/test.js'

        del os.environ["RETRACE_RUM_SCRIPT_URL"]

    def test_rum_script_url_invalid(self):
        os.environ["RETRACE_RUM_SCRIPT_URL"] = 'asd'

        config = Config()

        assert config.rum_script_url == 'https://stckjs.stackify.com/stckjs.js'  # Default

        del os.environ["RETRACE_RUM_SCRIPT_URL"]

    def test_rum_key_valid(self):
        os.environ["RETRACE_RUM_KEY"] = 'TEST123-_'

        config = Config()

        assert config.rum_key == 'TEST123-_'

        del os.environ["RETRACE_RUM_KEY"]

    def test_rum_key_invalid(self):
        os.environ["RETRACE_RUM_KEY"] = 'asd`1!'

        config = Config()

        assert config.rum_key == ''  # Default

        del os.environ["RETRACE_RUM_KEY"]

    def test_socket_url(self):
        os.environ["STACKIFY_TRANSPORT_SOCKET_PATH"] = 'test_socket_path'

        config = Config()

        assert config.socket_url == 'test_socket_path'

        del os.environ["STACKIFY_TRANSPORT_SOCKET_PATH"]

    def test_transport(self):
        os.environ["STACKIFY_TRANSPORT"] = 'test_transport'

        config = Config()

        assert config.transport == 'test_transport'
        del os.environ["STACKIFY_TRANSPORT"]

    def test_log_path(self):
        os.environ["STACKIFY_TRANSPORT_LOG_PATH"] = 'test_transport_log_path'

        config = Config()

        assert config.log_path == 'test_transport_log_path'

        del os.environ["STACKIFY_TRANSPORT_LOG_PATH"]

    def test_debug(self):
        os.environ["STACKIFY_DEBUG"] = 'True'

        config = Config()

        assert config.debug is True

        del os.environ["STACKIFY_DEBUG"]

    def test_queue(self):
        os.environ["STACKIFY_QUEUE"] = 'False'

        config = Config()

        assert config.queue is False

        del os.environ["STACKIFY_QUEUE"]

    def test_prefix_enabled(self):
        os.environ["STACKIFY_PREFIX_ENABLED"] = 'True'

        config = Config()

        assert config.queue is True

        del os.environ["STACKIFY_PREFIX_ENABLED"]
