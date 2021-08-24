import unittest

from lumipy.query.expression.sql_value_type import SqlValType
from test.test_utils import make_test_atlas, test_prefix_insertion


class TestVariadicScalarOp(unittest.TestCase):

    def setUp(self) -> None:
        self.atlas = make_test_atlas()
        self.table = self.atlas.lusid_logs_apprequest()
        self.test_col = self.atlas.lusid_logs_apprequest().duration
        self.test_str_col = self.atlas.lusid_logs_apprequest().application

    def test_simple_coalesce(self):

        # Create
        test_col = self.table.controller.coalesce("N/A")
        self.assertEqual(test_col.get_sql(), "coalesce([Controller], 'N/A')")
        self.assertEqual(test_col.get_type(), SqlValType.Text)

        # Test prefix insertion
        test_prefix_insertion(self, self.table, test_col)

    def test_complex_coalesce(self):

        # Create complex nonsense
        test_col = self.table.controller.coalesce(
            self.table.source_application,
            self.table.application,
            self.table.user_type,
            "unknown"
        )

        self.assertEqual(
            test_col.get_sql(),
            "coalesce([Controller], [SourceApplication], [Application], [UserType], 'unknown')"
        )
        self.assertEqual(test_col.get_type(), SqlValType.Text)

        # Test prefix insertion
        test_prefix_insertion(self, self.table, test_col)

    def test_coalesce_type_failure(self):
        with self.assertRaises(TypeError):
            self.table.controller.coalesce(125)

    def test_coalesce_wrong_args(self):
        with self.assertRaises(ValueError):
            self.table.controller.coalesce()