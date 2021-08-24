import unittest

from test.test_utils import make_test_atlas


class TestTernaryScalarOp(unittest.TestCase):

    def setUp(self) -> None:
        self.atlas = make_test_atlas()
        self.test_col = self.atlas.lusid_logs_apprequest().duration
        self.test_str_col = self.atlas.lusid_logs_apprequest().application

    def test_ternary_ops(self):
        between = self.test_col.between(0, 1)
        self.assertEqual(len(between.get_lineage()), 3)
        self.assertEqual(f'{self.test_col.get_sql()} BETWEEN 0 AND 1', between.get_sql())

        not_between = self.test_col.not_between(0, 1)
        self.assertEqual(len(between.get_lineage()), 3)
        self.assertEqual(f'{self.test_col.get_sql()} NOT BETWEEN 0 AND 1', not_between.get_sql())

    def test_substring_op(self):

        first_char = self.test_str_col.substr(1)
        self.assertEqual(first_char.get_sql(), 'substr([Application], 1, 1)')

        first_char = self.test_str_col.substr(1, 5)
        self.assertEqual(first_char.get_sql(), 'substr([Application], 1, 5)')

        first_char = self.test_str_col.substr(3, 5)
        self.assertEqual(first_char.get_sql(), 'substr([Application], 3, 5)')

        with self.assertRaises(ValueError) as ve:
            self.test_str_col.substr(0)
        self.assertIn("SQL substring index must be a positive non-zero int", str(ve.exception))
