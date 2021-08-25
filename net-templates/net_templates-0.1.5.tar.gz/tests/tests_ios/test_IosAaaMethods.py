import unittest
from tests.tests_ios.BaseTemplateTestIos import BaseTemplateTestIos
from net_models.models.services.cisco_ios.AaaMethods import *


class TestIosAaaAction(BaseTemplateTestIos):

    TEMPLATE_NAME = 'ios_aaa_action_list'

    def test_01(self):
        test_cases = [
            {
                "test_name": "Test-Local-01",
                "data": {
                    "params": [
                        {
                            "action": "local"
                        }
                    ]
                },
                "result": (
                    "local"
                )
            },
            {
                "test_name": "Test-Group-Local-01",
                "data": {
                    "params": [
                        {
                            "action": "group",
                            "group": "TACACS-GROUP"
                        },
                        {
                            "action": "local"
                        }
                    ]
                },
                "result": (
                    "group TACACS-GROUP local"
                )
            }
        ]
        super().common_testbase(test_cases=test_cases)


class TestIosAaaAuthentication(BaseTemplateTestIos):

    TEST_CLASS = IosAaaAuthentication
    TEMPLATE_NAME = 'ios_aaa_authentication'

    def test_01(self):
        test_cases = self.get_test_cases_from_resources()
        super().common_testbase(test_cases=test_cases)


class TestIosAaaAuthorization(BaseTemplateTestIos):

    TEST_CLASS = IosAaaAuthorization
    TEMPLATE_NAME = 'ios_aaa_authorization'

    def test_01(self):
        test_cases = self.get_test_cases_from_resources()
        super().common_testbase(test_cases=test_cases)


class TestIosAaaAccounting(BaseTemplateTestIos):

    TEST_CLASS = IosAaaAccounting
    TEMPLATE_NAME = 'ios_aaa_accounting'

    def test_01(self):
        test_cases = self.get_test_cases_from_resources()
        super().common_testbase(test_cases=test_cases)


class TestIosAaaConfig(BaseTemplateTestIos):

    TEST_CLASS = IosAaaConfig
    TEMPLATE_NAME = 'ios_aaa_config'

    def test_01(self):
        test_cases = self.get_test_cases_from_resources()
        super().common_testbase(test_cases=test_cases)