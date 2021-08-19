import unittest
from trifacta.transform_functions.function_definitions import ColumnFind


class TestColumnFind(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(ColumnFind(True, 0).exec("Hello", "ll"), 2)
        self.assertEqual(ColumnFind(True, 0).exec("Hello", "LL"), 2)

    def test_with_case_sensitive(self):
        self.assertEqual(ColumnFind(False, 0).exec("Hello", "LL"), None)

    def test_with_start(self):
        self.assertEqual(ColumnFind(True, 0).exec("banana", "na"), 2)
        self.assertEqual(ColumnFind(False, 4).exec("banana", "na"), 4)
        self.assertEqual(ColumnFind(False, 4).exec("banana", "NA"), None)

    def test_with_empty_input(self):
        self.assertEqual(ColumnFind(True, 0).exec("", "na"), None)
        self.assertEqual(ColumnFind(True, 0).exec("", ""), None)
        self.assertEqual(ColumnFind(True, 0).exec(None, ""), None)
        self.assertEqual(ColumnFind(True, 0).exec("", None), None)
        self.assertEqual(ColumnFind(True, 0).exec(None, None), None)

    def test_with_negative_start(self):
        self.assertEqual(ColumnFind(True, -1).exec("banana", "na"), None)

    def test_with_non_string(self):
        self.assertEqual(ColumnFind(True, 0).exec(1, 2), None)
        self.assertEqual(ColumnFind(True, 0).exec(1, True), None)


if __name__ == '__main__':
    unittest.main()
