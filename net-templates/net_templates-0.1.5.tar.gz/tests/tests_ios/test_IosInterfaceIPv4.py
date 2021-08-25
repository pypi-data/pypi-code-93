import unittest

from net_models.models import InterfaceIPv4Container, InterfaceIPv4Address


from .BaseTemplateTestIos import BaseTemplateTestIos


class TestIosInterfaceIpv4(BaseTemplateTestIos):

    TEMPLATE_NAME = 'ios_interface_ipv4'
    TEST_CLASS = InterfaceIPv4Container

    def test_01(self):
        test_cases = [
            {
                "test_name": "Test-01",
                "data": {
                    "params": InterfaceIPv4Container(
                        addresses=[
                            InterfaceIPv4Address(address="192.0.2.1/24"),
                            InterfaceIPv4Address(address="192.0.2.10/24", secondary=True)
                        ]
                    )
                },
                "result": (
                    " ip address 192.0.2.1 255.255.255.0\n"
                    " ip address 192.0.2.10 255.255.255.0 secondary\n"
                )
            }
        ]
        self.common_testbase(test_cases=test_cases)

if __name__ == '__main__':
    unittest.main()
