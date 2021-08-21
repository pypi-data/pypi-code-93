import unittest

from georgstage.app import App


class TestPlanner(unittest.TestCase):
    def setUp(self):
        self.app = App()

    def test_foo(self):
        self.assertEqual(self.app.foo(), 42)

if __name__ == '__main__':
    unittest.main()
