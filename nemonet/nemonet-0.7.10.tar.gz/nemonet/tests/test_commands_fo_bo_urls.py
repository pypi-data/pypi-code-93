# Created by Jan Rummens at 12/01/2021
import unittest
from nemonet.runner.vision_runner import Runner

class CommandsTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.runner = Runner(runner_config="runner_config.json")

    def tearDown(self) -> None:
        self.runner = None

    def test_open_formatted_url(self):
        self.runner.execute_scenario("commands-reformat-url")

if __name__ == '__main__':
    unittest.main()
