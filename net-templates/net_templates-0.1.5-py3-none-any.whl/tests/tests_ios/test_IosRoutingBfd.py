import unittest
from tests.tests_ios.BaseTemplateTestIos import BaseTemplateTestIos
from net_models.models.routing.RoutingProtocols import BfdTemplate, BfdAuthentication


class TestIosRoutingBfdTemplate(BaseTemplateTestIos):

    TEST_CLASS = BfdTemplate
    TEMPLATE_NAME = 'ios_routing_bfd_template'

    def test_01(self):
        test_cases = [
            {
                "test_name": "Test-BFD-Template-01",
                "data": {
                    "params": BfdTemplate(
                        name="BFD-Template-01",
                        type="single-hop",
                        min_rx=5,
                        min_tx=5,
                        multiplier=3,
                        authentication=BfdAuthentication(
                            method="md5",
                            keychain="Keychain-01"
                        )
                    )
                },
                "result": (
                    "bfd-template single-hop BFD-Template-01\n"
                    " interval min-tx 5 min-rx 5 multiplier 3\n"
                    " authentication md5 keychain Keychain-01\n"

                )
            },
            {
                "test_name": "Test-BFD-Template-02",
                "data": {
                    "params": BfdTemplate(
                        name="BFD-Template-02",
                        type="single-hop",
                        min_rx=5,
                        min_tx=5,
                        multiplier=3,
                        microseconds=True,
                        authentication=BfdAuthentication(
                            method="md5",
                            keychain="Keychain-01"
                        )
                    )
                },
                "result": (
                    "bfd-template single-hop BFD-Template-02\n"
                    " interval microseconds min-tx 5 min-rx 5 multiplier 3\n"
                    " authentication md5 keychain Keychain-01\n"

                )
            },
            {
                "test_name": "Test-BFD-Template-03",
                "data": {
                    "params": BfdTemplate(
                        name="BFD-Template-03",
                        type="single-hop",
                        both=5,
                        multiplier=3,
                        microseconds=True,
                        authentication=BfdAuthentication(
                            method="md5",
                            keychain="Keychain-01"
                        )
                    )
                },
                "result": (
                    "bfd-template single-hop BFD-Template-03\n"
                    " interval microseconds both 5 multiplier 3\n"
                    " authentication md5 keychain Keychain-01\n"

                )
            }
        ]
        super().common_testbase(test_cases=test_cases)


del BaseTemplateTestIos

if __name__ == '__main__':
    unittest.main()