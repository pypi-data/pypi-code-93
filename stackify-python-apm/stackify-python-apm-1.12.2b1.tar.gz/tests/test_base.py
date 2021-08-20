import os
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.base import Client

CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
}


class ClientTest(TestCase):

    def test_config_data(self):
        client = Client(CONFIG)

        assert client.config.environment == CONFIG["ENVIRONMENT"]
        assert client.config.hostname == CONFIG["HOSTNAME"]
        assert client.config.framework_name == CONFIG["FRAMEWORK_NAME"]
        assert client.config.framework_version == CONFIG["FRAMEWORK_VERSION"]
        assert client.config.application_name == CONFIG["APPLICATION_NAME"]
        assert client.config.base_dir == CONFIG["BASE_DIR"]

    def test_get_service_info(self):
        client = Client(CONFIG)
        service_info = client.get_service_info()

        assert service_info['name'] == 'service_name'
        assert service_info['environment'] == 'production'
        assert service_info['framework'] == {'name': 'framework', 'version': '1.0'}

    def test_get_process_info(self):
        client = Client(CONFIG)
        process_info = client.get_process_info()

        assert process_info['pid'] == os.getpid()
        assert process_info['ppid'] == os.getppid() if hasattr(os, "getppid") else None

    def test_get_system_info(self):
        client = Client(CONFIG)
        system_info = client.get_system_info()

        assert system_info['hostname']
        assert system_info['architecture']
        assert system_info['platform']

    def test_get_application_info(self):
        client = Client(CONFIG)
        application_info = client.get_application_info()

        assert application_info['application_name'] == 'sample_application'
        assert application_info['base_dir'] == 'path/to/application/'
        assert application_info['environment'] == 'production'

    def test_get_property_info_from_environment(self):
        client = Client(CONFIG)
        property_info = client.get_property_info_from_environment()

        assert property_info == {}

    def test_get_property_info_from_environment_with_data(self):
        os.environ["STACKIFY_ENV"] = "Ctest|CDtest|"
        os.environ["STACKIFY_RUM_DOMAIN"] = "some.domain"

        client = Client(CONFIG)
        property_info = client.get_property_info_from_environment()

        assert property_info == {
            "clientId": "Ctest",
            "deviceId": "CDtest",
            "clientRumDomain": "some.domain",
        }

    @mock.patch('stackifyapm.queue.QueueListener.enqueue')
    @mock.patch('stackifyapm.base.Client.transaction_handler')
    def test_none_queue_config(self, transaction_handler_mock, enqueue_mock):
        CONFIG.update({
            "QUEUE": False,
        })

        client = Client(CONFIG)
        client.queue('test')

        assert client.config.queue is False
        assert client.queue_listener is None
        assert not enqueue_mock.called
        assert transaction_handler_mock.called

    @mock.patch('stackifyapm.queue.QueueListener.enqueue')
    @mock.patch('stackifyapm.base.Client.transaction_handler')
    def test_queue_config(self, transaction_handler_mock, enqueue_mock):
        CONFIG.update({
            "QUEUE": True,
        })

        client = Client(CONFIG)
        client.queue('test')

        assert client.config.queue is True
        assert client.queue_listener
        assert enqueue_mock.called

    @mock.patch('stackifyapm.queue.QueueListener.stop')
    @mock.patch('stackifyapm.transport.Transport.send_all')
    def test_clean_up_with_queue(self, send_all_transport_mock, stop_queue_mock):
        CONFIG.update({
            "QUEUE": True,
        })

        client = Client(CONFIG)
        client.clean_up()

        assert stop_queue_mock.called
        assert send_all_transport_mock.called

    @mock.patch('stackifyapm.queue.QueueListener.stop')
    @mock.patch('stackifyapm.transport.Transport.send_all')
    def test_clean_up_without_queue(self, send_all_transport_mock, stop_queue_mock):
        CONFIG.update({
            "QUEUE": False,
        })

        client = Client(CONFIG)
        client.clean_up()

        assert not stop_queue_mock.called
        assert send_all_transport_mock.called
