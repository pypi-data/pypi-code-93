import unittest

from lumipy.query.expression.column.source_column import SourceColumn
from lumipy.query.expression.column_op.base_scalar_op import BaseScalarOp
from lumipy.query.expression.column_op.base_aggregation_op import BaseAggregateColumn
from lumipy.query.expression.sql_value_type import numerics, SqlValType
from test.test_utils import make_test_atlas


class TestAggregationOp(unittest.TestCase):

    def test_column_aggregations_on_provider_columns(self):

        atlas = make_test_atlas()

        for p_description in atlas.list_providers():

            p_hash = hash(p_description)

            for c_description in p_description.list_columns():
                col = SourceColumn(c_description, p_hash)

                # SUM - because the SQL name is different. We swap out sum for total so it behaves like pandas
                if col._type in numerics:
                    agg_col = col.sum()
                    self.assertTrue(col.get_sql() in agg_col.get_sql())
                    self.assertTrue('total' in agg_col.get_sql())
                    self.assertEqual(agg_col.source_table_hash(), col.source_table_hash())
                    self.assertEqual(agg_col.get_op_name(), "total")
                else:
                    with self.assertRaises(TypeError) as ar:
                        col.sum()
                    e = str(ar.exception)
                    self.assertTrue("Input types invalid for expression" in e)

                # OTHER NUMERICAL AGGREGATES
                numerical_aggregates = ['avg', 'median', 'stdev']
                for agg in numerical_aggregates:
                    if col._type in numerics:
                        agg_col = eval(f'col.{agg}()')
                        self.assertTrue(col.get_sql() in agg_col.get_sql())
                        self.assertTrue(agg in agg_col.get_sql())
                        self.assertEqual(agg_col.source_table_hash(), col.source_table_hash())
                        self.assertEqual(agg_col.get_op_name(), agg)
                    else:
                        with self.assertRaises(TypeError) as ar:
                            eval(f'col.{agg}()')
                        e = str(ar.exception)
                        self.assertTrue("Input types invalid for expression" in e)
                        self.assertTrue(agg in e)

                # Min/Max for anything. Everything should be able to be ordered?
                order_agg = ['min', 'max']
                for agg in order_agg:
                    if col._type in numerics:
                        agg_col = eval(f'col.{agg}()')
                        self.assertTrue(col.get_sql() in agg_col.get_sql())
                        self.assertTrue(agg in agg_col.get_sql())
                        self.assertEqual(agg_col.source_table_hash(), col.source_table_hash())
                        self.assertEqual(agg_col.get_op_name(), agg)

                # COUNT - should work for any data type
                if col._type in numerics:
                    agg_col = col.count()
                    self.assertTrue(col.get_sql() in agg_col.get_sql())
                    self.assertTrue('count' in agg_col.get_sql())
                    self.assertEqual(agg_col.source_table_hash(), col.source_table_hash())
                    self.assertEqual(agg_col.get_op_name(), "count")
                    self.assertEqual(agg_col.get_type(), SqlValType.Int)

    def test_aggregations_on_expressions(self):

        atlas = make_test_atlas()
        test_ops = {
            'mul': lambda x, y: x * y,
            'div': lambda x, y: x / y,
            'add': lambda x, y: x + y,
            'sub': lambda x, y: x - y,
            'mod': lambda x, y: x % y,
        }

        for p_description in atlas.list_providers():

            numeric_columns = [col for col in p_description.list_columns() if col.data_type in numerics]
            if len(numeric_columns) < 2:
                continue

            p_hash = hash(p_description)

            for i in range(len(numeric_columns) - 1):
                col1 = SourceColumn(numeric_columns[i], p_hash)
                col2 = SourceColumn(numeric_columns[i + 1], p_hash)

                for name, op in test_ops.items():

                    col3 = op(col1, col2)
                    self.assertTrue(
                        issubclass(type(col3), BaseScalarOp),
                        msg=f"Expected DerivedColumn type for col ({name}) col, but was {type(col3).__name__}."
                    )
                    sum_col3 = col3.sum()
                    self.assertTrue(issubclass(type(sum_col3), BaseAggregateColumn))
                    self.assertEqual(sum_col3.get_sql(), f"total({col3.get_sql()})")

                    # with rhs literal
                    col4 = op(col1, 2)
                    self.assertTrue(
                        issubclass(type(col4), BaseScalarOp),
                        msg=f"Expected DerivedColumn type for col ({name}) 2, but was {type(col4).__name__}."
                    )
                    sum_col4 = col4.sum()
                    self.assertTrue(issubclass(type(sum_col4), BaseAggregateColumn))
                    self.assertEqual(sum_col4.get_sql(), f"total({col4.get_sql()})")

                    # with lhs literal
                    col5 = op(2, col2)
                    self.assertTrue(
                        issubclass(type(col5), BaseScalarOp),
                        msg=f"Expected DerivedColumn type for 2 ({name}) col, but was {type(col5).__name__}."
                    )
                    sum_col5 = col5.sum()
                    self.assertTrue(issubclass(type(sum_col5), BaseAggregateColumn))
                    self.assertEqual(sum_col5.get_sql(), f"total({col5.get_sql()})")

    def test_quantile_aggregates(self):

        atlas = make_test_atlas()
        app_req = atlas.lusid_logs_apprequest()

        duration = app_req.duration
        from lumipy.query.expression.column_op.aggregation_op import Quantile
        qtl = Quantile(duration, 0.95)

        qtl_sql = qtl.get_sql()
        self.assertEqual(qtl_sql, "quantile([Duration], 0.95)")
        self.assertEqual(qtl_sql, duration.quantile(0.95).get_sql())
