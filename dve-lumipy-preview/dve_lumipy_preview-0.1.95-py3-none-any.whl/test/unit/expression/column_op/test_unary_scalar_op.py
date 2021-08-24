import unittest

from lumipy.query.expression.sql_value_type import SqlValType
from test.test_utils import make_test_atlas

import math


class TestUnaryScalarOp(unittest.TestCase):

    def setUp(self) -> None:
        self.atlas = make_test_atlas()
        self.test_col = self.atlas.lusid_logs_apprequest().duration
        self.test_bool = self.test_col > 1000
        self.test_text = self.atlas.lusid_logs_apprequest().method

    def test_not_expression(self):
        not_expr = ~self.test_bool
        self.assertEqual(not_expr.get_sql(), f"NOT ({self.test_bool.get_sql()})")
        self.assertEqual(len(not_expr.get_lineage()), 1)

    def test_is_null_expression(self):
        is_null_expr = self.test_col.is_null()
        self.assertEqual(is_null_expr.get_sql(), f"{self.test_col.get_sql()} IS NULL")
        self.assertEqual(len(is_null_expr.get_lineage()), 1)

    def test_negative_expression(self):
        neg_expr = -self.test_col
        self.assertEqual(neg_expr.get_sql(), f"-{self.test_col.get_sql()}")
        self.assertEqual(len(neg_expr.get_lineage()), 1)

    def test_case_expressions(self):

        # To TEXT (str)
        text_col = self.test_col.cast(str)
        self.assertEqual(text_col.get_sql(), f"cast({self.test_col.get_sql()} AS TEXT)")
        self.assertEqual(text_col.get_type(), SqlValType.Text)

        # To Int
        text_col = self.test_col.cast(int)
        self.assertEqual(text_col.get_sql(), f"cast({self.test_col.get_sql()} AS INT)")
        self.assertEqual(text_col.get_type(), SqlValType.Int)

        # To bool
        text_col = self.test_col.cast(bool)
        self.assertEqual(text_col.get_sql(), f"cast({self.test_col.get_sql()} AS BOOLEAN)")
        self.assertEqual(text_col.get_type(), SqlValType.Boolean)

        # To float
        text_col = self.test_col.cast(float)
        self.assertEqual(text_col.get_sql(), f"cast({self.test_col.get_sql()} AS DOUBLE)")
        self.assertEqual(text_col.get_type(), SqlValType.Double)

        # Fails with unsupported type
        with self.assertRaises(TypeError) as te:
            self.test_col.cast(list)
        self.assertIn('Invalid input to cast', te.exception.__str__())

        # Fails with input that isn't a type
        with self.assertRaises(TypeError) as te:
            self.test_col.cast(42)
        self.assertIn('Invalid input to cast', te.exception.__str__())

    def test_upper_case_expression(self):
        upper = self.test_text.upper()
        self.assertEqual(upper.get_sql(), f'Upper({self.test_text.get_sql()})')
        self.assertEqual(upper.get_type(), SqlValType.Text)

    def test_lower_case_expression(self):
        lower = self.test_text.lower()
        self.assertEqual(lower.get_sql(), f'Lower({self.test_text.get_sql()})')
        self.assertEqual(lower.get_type(), SqlValType.Text)

    def test_log_expression(self):
        log = self.test_col.log()
        self.assertEqual(log.get_sql(), f'log({self.test_col.get_sql()})')
        self.assertEqual(log.get_type(), SqlValType.Double)

    def test_log10_expression(self):
        log10 = self.test_col.log10()
        self.assertEqual(log10.get_sql(), f'log10({self.test_col.get_sql()})')
        self.assertEqual(log10.get_type(), SqlValType.Double)

    def test_exp_expression(self):
        exp = self.test_col.exp()
        self.assertEqual(exp.get_sql(), f'exp({self.test_col.get_sql()})')
        self.assertEqual(exp.get_type(), SqlValType.Double)

    def test_ceil_expression(self):

        seconds = self.test_col*0.001

        ceil1 = math.ceil(seconds)
        ceil2 = seconds.ceil()
        self.assertEqual(ceil1.get_sql(), ceil2.get_sql())
        self.assertEqual(ceil1.get_sql(), f'ceil({seconds.get_sql()})')
        self.assertEqual(ceil1.get_type(), SqlValType.Int)

    def test_floor_expression(self):
        seconds = self.test_col * 0.001

        floor1 = math.floor(seconds)
        floor2 = seconds.floor()
        self.assertEqual(floor1.get_sql(), floor2.get_sql())
        self.assertEqual(floor1.get_sql(), f'floor({seconds.get_sql()})')
        self.assertEqual(floor1.get_type(), SqlValType.Int)

    def test_abs_expression(self):

        seconds = self.test_col*0.001

        abs1 = abs(seconds)
        abs2 = seconds.abs()
        self.assertEqual(abs1.get_sql(), abs2.get_sql())
        self.assertEqual(abs1.get_sql(), f'abs({seconds.get_sql()})')
        self.assertEqual(abs1.get_type(), SqlValType.Double)
        self.assertEqual(abs(self.test_col.cast(int)).get_type(), SqlValType.Int)
