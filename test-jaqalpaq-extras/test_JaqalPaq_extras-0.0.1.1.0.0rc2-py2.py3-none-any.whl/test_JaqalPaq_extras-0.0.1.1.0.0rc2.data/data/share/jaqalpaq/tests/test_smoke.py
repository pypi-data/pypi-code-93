import unittest


class SmokeTester(unittest.TestCase):
    def test_smoketest(self):
        # Simple test to confirm that we can import both the
        # man JaqalPaq packages, and the extras here.
        import jaqalpaq.core
        import jaqalpaq
        import jaqalpaq.transpilers
        import jaqalpaq.parser
