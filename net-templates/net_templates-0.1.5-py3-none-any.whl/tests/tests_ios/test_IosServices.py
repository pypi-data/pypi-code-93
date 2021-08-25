import unittest
from tests.tests_ios.BaseTemplateTestIos import BaseTemplateTestIos
from net_models.models.BaseModels.SharedModels import KeyBase
from net_models.models.services.ServerModels import (
    TacacsServer,
    TacacsServerGroup,
    RadiusServer,
    RadiusServerGroup
)

class TestIosTacacsServer(BaseTemplateTestIos):

    TEMPLATE_NAME = 'ios_aaa_server_tacacs'

    def test_01(self):
        test_cases = [
            {
                "test_name": "Test-01",
                "data": {
                    "params": TacacsServer(
                        name="TACACS-01",
                        server="1.2.3.4",
                        key=KeyBase(
                            encryption_type="0",
                            value="P@ssw0rd"
                        ),
                        single_connection=True
                    )
                },
                "result": (
                    "tacacs server TACACS-01\n"
                    " address ipv4 1.2.3.4\n"
                    " key 0 P@ssw0rd\n"
                    " single-connection\n"
                )
            }
        ]
        super().common_testbase(test_cases=test_cases)


class TestIosTacacsServerGroup(BaseTemplateTestIos):

    TEST_CLASS = TacacsServerGroup
    TEMPLATE_NAME = 'ios_aaa_group_tacacs'

    def test_01(self):
        test_cases = self.get_test_cases_from_resources()
        super().common_testbase(test_cases=test_cases)


class TestIosTacacsAll(BaseTemplateTestIos):

    TEST_CLASS = TacacsServerGroup
    TEMPLATE_NAME = 'ios_aaa_tacacs_all'

    def test_01(self):
        test_cases = self.get_test_cases_from_resources()
        super().common_testbase(test_cases=test_cases)


class TestIosRadiusServer(BaseTemplateTestIos):

    TEST_CLASS = RadiusServer
    TEMPLATE_NAME = 'ios_aaa_server_radius'

    def test_01(self):
        test_cases = [
            {
                "test_name": "Test-01",
                "data": {
                    "params": RadiusServer(
                        name="RADIUS-01",
                        server="192.0.2.1",
                        key=KeyBase(
                            encryption_type="0",
                            value="SecretPassword"
                        ),
                        single_connection=True
                    )
                },
                "result": (
                    "radius server RADIUS-01\n"
                    " address ipv4 192.0.2.1\n"
                    " key 0 SecretPassword\n"
                    " single-connection\n"
                )
            }
        ]
        super().common_testbase(test_cases=test_cases)


class TestIosRadiusServerGroup(BaseTemplateTestIos):

    TEST_CLASS = RadiusServerGroup
    TEMPLATE_NAME = 'ios_aaa_group_radius'

    def test_01(self):
        test_cases = self.get_test_cases_from_resources()
        super().common_testbase(test_cases=test_cases)


class TestIosRadiusAll(BaseTemplateTestIos):

    TEST_CLASS = RadiusServerGroup
    TEMPLATE_NAME = 'ios_aaa_radius_all'

    def test_01(self):
        test_cases = self.get_test_cases_from_resources()
        super().common_testbase(test_cases=test_cases)

if __name__ == '__main__':
    unittest.main()