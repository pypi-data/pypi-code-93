# Created by Jan Rummens at 12/01/2021
import unittest
from nemonet.runner.vision_runner import Runner

class CommandsTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.runner = Runner(runner_config="runner_config.json")

    def tearDown(self) -> None:
        self.runner = None

    def test_chrome_options(self):
        self.runner.execute_scenario("dummy")

    def test_save_records(self):
        self.runner.execute_scenario("commands-save-records")

    def test_double_click(self):
        self.runner.execute_scenario("commands-double-mouse-click")

    def test_drag_and_drop(self):
        self.runner.execute_scenario("commands-drag-and-drop")

    def test_drag_and_drop_mouse(self):
        self.runner.execute_scenario("commands-drag-and-drop-mouse")

    def test_drag_and_drop_offset(self):
        self.runner.execute_scenario("commands-drag-and-drop-offset")

    def test_explicit_waits(self):
        self.runner.execute_scenario("commands-explicit-waits")

    def test_remove_html_element(self):
        self.runner.execute_scenario("commands-remove-html-element")

    def test_right_mouse(self):
        self.runner.execute_scenario("command-right-mouse")

    def test_tabs(self):
        self.runner.execute_scenario("command-tabs")

    def test_current_pos(self):
        self.runner.execute_scenario("command-current-pos")

if __name__ == '__main__':
    unittest.main()
