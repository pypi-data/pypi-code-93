import unittest

from src.parsec import BasicState, string


class TestTextParsers(unittest.TestCase):
    def test_text(self):
        content = "this is a simple string"
        state = BasicState(content)
        p = string("this")
        self.assertEqual(p(state), "this")

    def test_case(self):
        state = BasicState("this is a simple string")
        p = string("THIS", False)
        self.assertEqual(p(state), "this")

        state = BasicState("This is a simple string")
        p = string("this", False)
        self.assertEqual(p(state), "This")


if __name__ == "__main__":
    unittest.main()
