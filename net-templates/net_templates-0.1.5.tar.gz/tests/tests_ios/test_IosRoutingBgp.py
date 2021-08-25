import unittest
from tests.tests_ios.BaseTemplateTestIos import BaseTemplateTestIos
from net_models.models.routing.BgpModels import BgpNeighborBase, RoutingBgpProcess


class TestIosRoutingBgpProcess(BaseTemplateTestIos):

    TEST_CLASS = RoutingBgpProcess
    TEMPLATE_NAME = 'ios_routing_bgp'

    def test_01(self):
        test_cases = self.get_test_cases_from_resources()
        super().common_testbase(test_cases=test_cases)


del BaseTemplateTestIos

if __name__ == '__main__':
    unittest.main()