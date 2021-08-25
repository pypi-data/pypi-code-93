import unittest

from net_models.models.BaseModels.SharedModels import VRFModel

from tests.tests_ios.BaseTemplateTestIos import BaseTemplateTestIos


class TestIosVrfDefinition(BaseTemplateTestIos):

    TEMPLATE_NAME = 'ios_vrf_definition'
    TEST_CLASS = VRFModel

    def test_resources(self):
        self.common_testbase(test_cases=self.get_test_cases_from_resources())


class TestIosVrfDefinitions(BaseTemplateTestIos):

    TEMPLATE_NAME = 'ios_vrf_definition_all'

    def test_resources(self):
        self.common_testbase(test_cases=self.get_test_cases_from_resources())

del BaseTemplateTestIos

if __name__ == '__main__':
    unittest.main()