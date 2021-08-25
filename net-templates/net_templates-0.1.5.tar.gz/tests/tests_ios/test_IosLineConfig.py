import unittest
from tests.tests_ios.BaseTemplateTestIos import BaseTemplateTestIos
from net_models.models.services.cisco_ios.IosLineModels import *


class TestIosLineConfig(BaseTemplateTestIos):

    TEST_CLASS = IosLineConfig
    TEMPLATE_NAME = 'ios_line_config'

    def test_resources(self):
        test_cases = self.get_test_cases_from_resources()
        super().common_testbase(test_cases=test_cases)


if __name__ == '__main__':
    unittest.main()