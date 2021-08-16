# Created by Jan Rummens at 19/01/2021
import unittest

from nemonet.engines.reporter import Reporter

class ReporterTestCase(unittest.TestCase):

    def test_zephyr(self):
        reporter = Reporter()
        reporter.publish("dummy_zephyr", Reporter.status_failed)


if __name__ == '__main__':
    unittest.main()
