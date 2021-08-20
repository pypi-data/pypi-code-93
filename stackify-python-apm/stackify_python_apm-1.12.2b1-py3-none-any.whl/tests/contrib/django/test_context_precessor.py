from stackifyapm.contrib.django.context_processors import rum_tracing
from stackifyapm.base import Client
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

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
    "RUM_SCRIPT_URL": "https://test.com/test.js",
    "RUM_KEY": "LOREM123"
}


class DangoRumTracingTest(TestCase):

    def test_rum_tracing_no_transaction(self):

        rum_data = rum_tracing('request')

        assert rum_data == {}

    @mock.patch('stackifyapm.base.Client.get_property_info')
    def test_rum_tracing_with_transaction(self, get_property_info_mock):
        get_property_info_mock.return_value = {"deviceId": "Device ID", "clientId": "Client ID", "clientRumDomain": "Client Rum Domain"}
        self.client = Client(CONFIG)

        transaction = self.client.begin_transaction("transaction_test", client=self.client)

        rum_data = rum_tracing('request')

        assert rum_data
        assert rum_data['stackifyapm_inject_rum']

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
        assert rum_data['stackifyapm_inject_rum'] == result_string
