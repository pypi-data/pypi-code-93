from stackifyapm.base import Client
from stackifyapm import insert_rum_script
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

import base64
import json
from stackifyapm.traces import set_transaction_context


CONFIG = {
    "SERVICE_NAME": "service_name",
    "ENVIRONMENT": "production",
    "HOSTNAME": "sample_host",
    "FRAMEWORK_NAME": "framework",
    "FRAMEWORK_VERSION": "1.0",
    "APPLICATION_NAME": "sample_application",
    "BASE_DIR": "path/to/application/",
    "RUM_SCRIPT_URL": "https://test.com/test.js",
    "RUM_KEY": "LOREM123"
}


class ManualRumTracingTest(TestCase):

    def test_insert_rum_script_no_transaction(self):
        rum_data = insert_rum_script()
        assert rum_data is None

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_insert_rum_script_with_transaction(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.client = Client(CONFIG)

        transaction = self.client.begin_transaction("transaction_test", client=self.client)

        rum_data = insert_rum_script()
        assert rum_data

        rum_settings = {
            "ID": transaction.get_trace_parent().trace_id,
            "Name": base64.b64encode(CONFIG["APPLICATION_NAME"].encode("utf-8")).decode("utf-8"),
            "Env": base64.b64encode(CONFIG["ENVIRONMENT"].encode("utf-8")).decode("utf-8"),
            "Trans": base64.b64encode('/'.encode("utf-8")).decode("utf-8")
        }

        result_string = '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="{}" data-key="{}" async></script>'.format(
            json.dumps(rum_settings),
            CONFIG["RUM_SCRIPT_URL"],
            CONFIG["RUM_KEY"]
        )
        assert rum_data == result_string

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_insert_rum_script_with_transaction_reporting_url(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.client = Client(CONFIG)

        transaction = self.client.begin_transaction("transaction_test", client=self.client)
        set_transaction_context("/test-reporting-url", "reporting_url")
        rum_data = insert_rum_script()
        assert rum_data

        rum_settings = {
            "ID": transaction.get_trace_parent().trace_id,
            "Name": base64.b64encode(CONFIG["APPLICATION_NAME"].encode("utf-8")).decode("utf-8"),
            "Env": base64.b64encode(CONFIG["ENVIRONMENT"].encode("utf-8")).decode("utf-8"),
            "Trans": base64.b64encode("/test-reporting-url".encode("utf-8")).decode("utf-8")
        }

        result_string = '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="{}" data-key="{}" async></script>'.format(
            json.dumps(rum_settings),
            CONFIG["RUM_SCRIPT_URL"],
            CONFIG["RUM_KEY"]
        )
        assert rum_data == result_string

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_insert_rum_script_with_transaction_reporting_url_with_method(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.client = Client(CONFIG)

        transaction = self.client.begin_transaction("transaction_test", client=self.client)
        set_transaction_context("/test-reporting-url", "reporting_url")
        set_transaction_context({
            "method": "GET"
        }, "request")

        rum_data = insert_rum_script()
        assert rum_data

        rum_settings = {
            "ID": transaction.get_trace_parent().trace_id,
            "Name": base64.b64encode(CONFIG["APPLICATION_NAME"].encode("utf-8")).decode("utf-8"),
            "Env": base64.b64encode(CONFIG["ENVIRONMENT"].encode("utf-8")).decode("utf-8"),
            "Trans": base64.b64encode("GET-/test-reporting-url".encode("utf-8")).decode("utf-8")
        }

        result_string = '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="{}" data-key="{}" async></script>'.format(
            json.dumps(rum_settings),
            CONFIG["RUM_SCRIPT_URL"],
            CONFIG["RUM_KEY"]
        )
        assert rum_data == result_string

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_insert_rum_script_with_transaction_reporting_url_with_method_and_masking(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.client = Client(CONFIG)

        transaction = self.client.begin_transaction("transaction_test", client=self.client)
        set_transaction_context("/192.168.0.1/12/2d64ec54-06ec-4d41-9499-3eb218693a07/test-email.test+01@gmail.com/asd;asd/asdfsdfsdf/", "reporting_url")
        set_transaction_context({
            "method": "GET"
        }, "request")

        rum_data = insert_rum_script()
        assert rum_data

        rum_settings = {
            "ID": transaction.get_trace_parent().trace_id,
            "Name": base64.b64encode(CONFIG["APPLICATION_NAME"].encode("utf-8")).decode("utf-8"),
            "Env": base64.b64encode(CONFIG["ENVIRONMENT"].encode("utf-8")).decode("utf-8"),
            "Trans": base64.b64encode("GET-/{ip}/{id}/{guid}/{email}/asd/asdfsdfsdf".encode("utf-8")).decode("utf-8")
        }

        result_string = '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="{}" data-key="{}" async></script>'.format(
            json.dumps(rum_settings),
            CONFIG["RUM_SCRIPT_URL"],
            CONFIG["RUM_KEY"]
        )
        assert rum_data == result_string

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_insert_rum_script_with_transaction_reporting_url_with_method_root_path(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.client = Client(CONFIG)

        transaction = self.client.begin_transaction("transaction_test", client=self.client)
        set_transaction_context("/", "reporting_url")
        set_transaction_context({
            "method": "GET"
        }, "request")

        rum_data = insert_rum_script()
        assert rum_data

        rum_settings = {
            "ID": transaction.get_trace_parent().trace_id,
            "Name": base64.b64encode(CONFIG["APPLICATION_NAME"].encode("utf-8")).decode("utf-8"),
            "Env": base64.b64encode(CONFIG["ENVIRONMENT"].encode("utf-8")).decode("utf-8"),
            "Trans": base64.b64encode("GET-/".encode("utf-8")).decode("utf-8")
        }

        result_string = '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="{}" data-key="{}" async></script>'.format(
            json.dumps(rum_settings),
            CONFIG["RUM_SCRIPT_URL"],
            CONFIG["RUM_KEY"]
        )
        assert rum_data == result_string

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_insert_rum_script_with_transaction_reporting_url_with_method_root_path_empty(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.client = Client(CONFIG)

        transaction = self.client.begin_transaction("transaction_test", client=self.client)
        set_transaction_context({
            "method": "GET"
        }, "request")

        rum_data = insert_rum_script()
        assert rum_data

        rum_settings = {
            "ID": transaction.get_trace_parent().trace_id,
            "Name": base64.b64encode(CONFIG["APPLICATION_NAME"].encode("utf-8")).decode("utf-8"),
            "Env": base64.b64encode(CONFIG["ENVIRONMENT"].encode("utf-8")).decode("utf-8"),
            "Trans": base64.b64encode("GET-/".encode("utf-8")).decode("utf-8")
        }

        result_string = '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="{}" data-key="{}" async></script>'.format(
            json.dumps(rum_settings),
            CONFIG["RUM_SCRIPT_URL"],
            CONFIG["RUM_KEY"]
        )
        assert rum_data == result_string

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_insert_rum_script_with_transaction_reporting_url_without_method_and_masking(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.client = Client(CONFIG)

        transaction = self.client.begin_transaction("transaction_test", client=self.client)
        set_transaction_context("/192.168.0.1/12/2d64ec54-06ec-4d41-9499-3eb218693a07/test-email.test+01@gmail.com/asd;asd/asdfsdfsdf/", "reporting_url")

        rum_data = insert_rum_script()
        assert rum_data

        rum_settings = {
            "ID": transaction.get_trace_parent().trace_id,
            "Name": base64.b64encode(CONFIG["APPLICATION_NAME"].encode("utf-8")).decode("utf-8"),
            "Env": base64.b64encode(CONFIG["ENVIRONMENT"].encode("utf-8")).decode("utf-8"),
            "Trans": base64.b64encode("/{ip}/{id}/{guid}/{email}/asd/asdfsdfsdf".encode("utf-8")).decode("utf-8")
        }

        result_string = '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="{}" data-key="{}" async></script>'.format(
            json.dumps(rum_settings),
            CONFIG["RUM_SCRIPT_URL"],
            CONFIG["RUM_KEY"]
        )
        assert rum_data == result_string

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_insert_rum_script_with_transaction_reporting_url_without_method_root_path(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.client = Client(CONFIG)

        transaction = self.client.begin_transaction("transaction_test", client=self.client)
        set_transaction_context("/", "reporting_url")

        rum_data = insert_rum_script()
        assert rum_data

        rum_settings = {
            "ID": transaction.get_trace_parent().trace_id,
            "Name": base64.b64encode(CONFIG["APPLICATION_NAME"].encode("utf-8")).decode("utf-8"),
            "Env": base64.b64encode(CONFIG["ENVIRONMENT"].encode("utf-8")).decode("utf-8"),
            "Trans": base64.b64encode("/".encode("utf-8")).decode("utf-8")
        }

        result_string = '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="{}" data-key="{}" async></script>'.format(
            json.dumps(rum_settings),
            CONFIG["RUM_SCRIPT_URL"],
            CONFIG["RUM_KEY"]
        )
        assert rum_data == result_string

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_insert_rum_script_with_transaction_reporting_url_without_method_root_path_empty(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.client = Client(CONFIG)

        transaction = self.client.begin_transaction("transaction_test", client=self.client)

        rum_data = insert_rum_script()
        assert rum_data

        rum_settings = {
            "ID": transaction.get_trace_parent().trace_id,
            "Name": base64.b64encode(CONFIG["APPLICATION_NAME"].encode("utf-8")).decode("utf-8"),
            "Env": base64.b64encode(CONFIG["ENVIRONMENT"].encode("utf-8")).decode("utf-8"),
            "Trans": base64.b64encode("/".encode("utf-8")).decode("utf-8")
        }

        result_string = '<script type="text/javascript">(window.StackifySettings || (window.StackifySettings = {}))</script><script src="{}" data-key="{}" async></script>'.format(
            json.dumps(rum_settings),
            CONFIG["RUM_SCRIPT_URL"],
            CONFIG["RUM_KEY"]
        )
        assert rum_data == result_string
