from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackifyapm.base import Client
from stackifyapm.traces import execution_context
from stackifyapm.utils.helper import get_current_time_in_millis
from stackifyapm.utils.helper import get_current_time_in_string
from stackifyapm.utils.helper import get_rum_script_or_none
from stackifyapm.utils.helper import mask_string
from stackifyapm.utils.helper import mask_reporting_url

import base64
import json

CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
    "RUMV2_ENABLED": True,
    "RUM_SCRIPT_URL": "https://test.com/test.js",
    "RUM_KEY": ""
}


class TestGetCurrentTimeInMillis(TestCase):

    def test_should_be_float(self):
        time = get_current_time_in_millis()

        assert isinstance(time, float)

    def test_should_contain_at_least_13_characters(self):
        time = str(get_current_time_in_millis())

        assert len(time) >= 13

    def test_should_contain_decemal_point(self):
        time = str(get_current_time_in_millis())

        assert time.count('.') == 1


class TestGetCurrentTimeInString(TestCase):

    def test_should_be_string(self):
        time = get_current_time_in_string()

        assert isinstance(time, str)

    def test_should_be_13_characters(self):
        time = get_current_time_in_string()

        assert len(time) == 13

    def test_should_not_contain_decemal_point(self):
        time = get_current_time_in_string()

        assert time.count('.') == 0


class TestRumTracing(TestCase):
    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_rum_tracing_disabled(self, get_property_info_mock):
        get_property_info_mock.return_value = {}
        default_rum_v2 = CONFIG['RUMV2_ENABLED']
        CONFIG['RUMV2_ENABLED'] = False
        self.client = Client(CONFIG)
        CONFIG['RUMV2_ENABLED'] = default_rum_v2

        self.client.begin_transaction("transaction_test", client=self.client)
        transaction = execution_context.get_transaction()

        rum_data = get_rum_script_or_none(transaction)

        assert not rum_data
        assert rum_data is ''

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_rum_tracing_has_empty_rum_key(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientRumDomain": "Client Rum Domain"}
        config = CONFIG
        config["RUM_KEY"] = ""
        self.client = Client(config)

        self.client.begin_transaction("transaction_test", client=self.client)
        transaction = execution_context.get_transaction()
        rum_data = get_rum_script_or_none(transaction)

        assert not rum_data
        assert rum_data is ''

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_rum_tracing_has_only_rum_key(self, get_property_info_mock):
        config = CONFIG
        self.client = Client(config)
        self.client.config.rum_key = "LOREM123"

        self.client.begin_transaction("transaction_test", client=self.client)
        transaction = execution_context.get_transaction()

        rum_data = get_rum_script_or_none(transaction)

        assert rum_data

        rum_settings = {
            "ID": transaction.get_trace_parent().trace_id,
            "Name": base64.b64encode(CONFIG["APPLICATION_NAME"].encode("utf-8")).decode("utf-8"),
            "Env": base64.b64encode(CONFIG["ENVIRONMENT"].encode("utf-8")).decode("utf-8"),
            "Trans": base64.b64encode('/'.encode("utf-8")).decode("utf-8")
        }

        expected_return = '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="{}" data-key="{}" async></script>'.format(
            json.dumps(rum_settings),
            CONFIG["RUM_SCRIPT_URL"],
            self.client.config.rum_key
        )

        assert rum_data == expected_return

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_rum_tracing_with_transaction(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.client = Client(CONFIG)
        self.client.config.rum_key = "LOREM123"

        transaction = self.client.begin_transaction("transaction_test", client=self.client)
        rum_data = get_rum_script_or_none(transaction)

        assert rum_data

        rum_settings = {
            "ID": transaction.get_trace_parent().trace_id,
            "Name": base64.b64encode(CONFIG["APPLICATION_NAME"].encode("utf-8")).decode("utf-8"),
            "Env": base64.b64encode(CONFIG["ENVIRONMENT"].encode("utf-8")).decode("utf-8"),
            "Trans": base64.b64encode('/'.encode("utf-8")).decode("utf-8"),
        }

        expected_return = '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="{}" data-key="{}" async></script>'.format(
            json.dumps(rum_settings),
            CONFIG["RUM_SCRIPT_URL"],
            self.client.config.rum_key
        )

        assert rum_data == expected_return


class TestMaskString(TestCase):

    def test_should_mask_ip(self):
        masked_string = mask_string('192.168.0.1')
        assert masked_string == '{ip}'

    def test_should_mask_guid(self):
        masked_string = mask_string('2d64ec54-06ec-4d41-9499-3eb218693a07')
        assert masked_string == '{guid}'

    def test_should_mask_email(self):
        masked_string = mask_string('test-email.test+01@gmail.com')
        assert masked_string == '{email}'

    def test_should_mask_id(self):
        masked_string = mask_string('123')
        assert masked_string == '{id}'

    def test_should_truncate_semicolon(self):
        masked_string = mask_string('asd;asd')
        assert masked_string == 'asd'


class TestMaskReportingUrl(TestCase):

    def test_should_mask_reporting_url(self):
        payload = '/192.168.0.1/12/2d64ec54-06ec-4d41-9499-3eb218693a07/test-email.test+01@gmail.com/asd;asd/asdfsdfsdf/'
        masked_string = mask_reporting_url(payload)
        assert masked_string == '/{ip}/{id}/{guid}/{email}/asd/asdfsdfsdf'

    def test_should_mask_reporting_url_root_path(self):
        payload = '/'
        masked_string = mask_reporting_url(payload)
        assert masked_string == '/'

    def test_should_mask_reporting_url_root_path_empty(self):
        payload = ''
        masked_string = mask_reporting_url(payload)
        assert masked_string == '/'
