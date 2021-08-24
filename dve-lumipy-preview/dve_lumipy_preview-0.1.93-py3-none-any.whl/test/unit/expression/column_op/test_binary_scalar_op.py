import unittest

from lumipy.query.expression.column.source_column import SourceColumn
from lumipy.query.expression.sql_value_type import SqlValType, numerics
from test.test_utils import make_test_atlas, test_prefix_insertion, standardise_sql_string


class TestColumnBinaryScalarOp(unittest.TestCase):

    def setUp(self) -> None:
        self.atlas = make_test_atlas()
        self.appreq = self.atlas.lusid_logs_apprequest()
        self.rtrace = self.atlas.lusid_logs_requesttrace()
        self.test_text_col = self.appreq.request_id
        self.test_double_col = self.appreq.duration
        self.test_int_col = self.appreq.error_code.cast(int)

    def test_is_in_variants(self):

        other = self.appreq.select(self.appreq.request_id).where(
            self.appreq.duration > 1000
        ).to_table_var('other')

        is_in_sql = self.appreq.request_id.is_in(other.select(other.request_id)).get_sql()

        test_sql = self.appreq.select('^').where(
            self.appreq.request_id.is_in(
                other.select(other.request_id)
            )
        ).get_sql()
        pass

    def test_new_scalar_op_base(self):

        duration = self.appreq.duration
        test = (duration + 1) + 100
        test_sql = test.get_sql()

        self.assertEqual(test_sql, '([Duration] + 1) + 100')

    def test_is_in_with_list(self):

        is_in_sql = self.appreq.application.is_in(['shrine', 'lusid']).get_sql()
        self.assertEqual(is_in_sql, "[Application] IN ('shrine', 'lusid')")

    def test_membership_container(self):

        from lumipy.query.expression.column.collection import CollectionExpression

        container1 = CollectionExpression(self.appreq.select(self.appreq.duration))
        container1_sql = container1.get_sql()
        self.assertEqual(
            standardise_sql_string(container1_sql),
            standardise_sql_string("(SELECT [Duration] FROM Lusid.Logs.AppRequest)")
        )

        container2 = CollectionExpression(*["a", "b", "c"])
        container2_sql = container2.get_sql()

        self.assertEqual(container2_sql, "('a', 'b', 'c')")

    def test_is_in_prefixing_reconstruction(self):

        appreq_alias = self.appreq.with_alias('test')
        rtrace_alias = self.rtrace.with_alias('RT')

        is_in = self.appreq.application.is_in(['shrine', 'lusid'])
        prfx_is_in = appreq_alias.apply_prefix(is_in)

        sql_prfx_is_in = prfx_is_in.get_sql()
        self.assertEqual(sql_prfx_is_in, "test.[Application] IN ('shrine', 'lusid')")

        rids = self.appreq.select('*').where(self.appreq.duration > 10000).to_table_var('rids').with_alias('RIDS')

        cndn = self.rtrace.request_id.is_in(rids.select(rids.request_id))
        prfx_cndn = rids.apply_prefix(rtrace_alias.apply_prefix(cndn))

        prfx_cndn_sql = prfx_cndn.get_sql()
        self.assertEqual(
            standardise_sql_string(prfx_cndn_sql),
            standardise_sql_string('RT.[RequestId] IN (SELECT RIDS.[RequestId] FROM @rids AS RIDS)')
        )

    # noinspection SpellCheckingInspection
    def test_numeric_binary_op_source_and_literal_cols(self):

        const = 2.0
        test_ops = {
            'mul': lambda x: x * const,
            'div': lambda x: x / const,
            'add': lambda x: x + const,
            'sub': lambda x: x - const,
            'mod': lambda x: x % const,
        }

        for p_description in self.atlas.list_providers():

            p_hash = hash(p_description)

            for c_description in p_description.list_columns():

                if c_description.data_type in numerics:
                    for name, op in test_ops.items():
                        col = SourceColumn(c_description, p_hash)
                        expr = op(col)

                        self.assertEqual(len(expr.get_lineage()), 2)

                if c_description.data_type == SqlValType.Text:
                    col = SourceColumn(c_description, p_hash)
                    expr = col.concat('_ABCD')

                    self.assertEqual(len(expr.get_lineage()), 2)

    def test_numeric_binary_op_two_source_cols(self):

        test_ops = {
            'mul': lambda x, y: x * y,
            'div': lambda x, y: x / y,
            'add': lambda x, y: x + y,
            'sub': lambda x, y: x - y,
            'mod': lambda x, y: x % y,
        }

        for p_description in self.atlas.list_providers():
            p_hash = hash(p_description)
            numeric_fields = [SourceColumn(c, p_hash) for c in p_description.list_columns() if c.data_type in numerics]
            for col1 in numeric_fields:
                for col2 in numeric_fields:
                    for name, op in test_ops.items():
                        expr = op(col1, col2)
                        self.assertEqual(expr.source_table_hash(), col1.source_table_hash())
                        self.assertEqual(len(expr.get_lineage()), 2)

    def test_degenerate_expression_args_bug(self):

        provider1 = self.atlas.lusid_logs_apprequest()
        provider2 = self.atlas.lusid_logs_apprequest()
        v1 = provider1.duration / 2
        v2 = provider2.duration / 2

        v3 = v1 + v2
        self.assertEqual(v3.get_sql(), f"({v1.get_sql()}) + ({v2.get_sql()})")

    def test_regexp_binary_op_sql(self):

        pattern = '^.*?$'
        self.assertEqual(self.test_text_col.regexp(pattern).get_sql(),
                         f"{self.test_text_col.get_sql()} REGEXP '{pattern}'")
        self.assertEqual(self.test_text_col.not_regexp(pattern).get_sql(),
                         f"{self.test_text_col.get_sql()} NOT REGEXP '{pattern}'")
        self.assertRaises(TypeError, lambda p: self.test_double_col.regexp(p), pattern)
        self.assertRaises(TypeError, lambda p: self.test_double_col.not_regexp(p), pattern)

    def test_power_expressions(self):

        # Test expressions raised to a power
        for n in range(5):
            int_pow = self.test_int_col**n
            self.assertEqual(int_pow.get_sql(), f'power(({self.test_int_col.get_sql()}), {n})')
            self.assertEqual(int_pow.get_type(), SqlValType.Int)

            dbl_pow = self.test_double_col ** n
            self.assertEqual(dbl_pow.get_sql(), f'power({self.test_double_col.get_sql()}, {n})')
            self.assertEqual(dbl_pow.get_type(), SqlValType.Double)

        # Test literals raised to the power of an expression
        two_to_dbl = 2**self.test_double_col
        self.assertEqual(two_to_dbl.get_sql(), f'power(2, {self.test_double_col.get_sql()})')
        self.assertEqual(two_to_dbl.get_type(), SqlValType.Double)

        two_to_int = 2**self.test_int_col
        self.assertEqual(two_to_int.get_sql(), f'power(2, ({self.test_int_col.get_sql()}))')
        self.assertEqual(two_to_int.get_type(), SqlValType.Int)

    def test_round_expression(self):

        # No number of places specified evals to zero places
        round_none1 = self.test_double_col.round()
        round_none2 = round(self.test_double_col)
        self.assertEqual(round_none2.get_sql(), round_none1.get_sql())
        self.assertEqual(round_none1.get_type(), SqlValType.Double)
        self.assertEqual(round_none1.get_sql(), f"round({self.test_double_col.get_sql()}, 0)")

        for n in range(3):
            rounded = round(self.test_double_col, n)
            self.assertEqual(rounded.get_sql(), f'round({self.test_double_col.get_sql()}, {n})')

    def test_cast_in_prefix_insertion(self):
        test_prefix_insertion(self, self.appreq, (self.appreq.duration*0.001).cast(int))

    def test_round_in_prefix_insertion(self):
        test_prefix_insertion(self, self.appreq, round(self.appreq.duration*0.001))

    def test_power_in_prefix_insertion(self):
        test_prefix_insertion(self, self.appreq, self.appreq.duration ** 3)

    def test_pad_string(self):

        pad_r = self.test_text_col.pad_str(9, 'right')
        self.assertEqual(pad_r, 'padr([RequestId], 9)')
        test_prefix_insertion(self, self.appreq, pad_r)

        pad_l = self.test_text_col.pad_str(9, 'left')
        test_prefix_insertion(self, self.appreq, pad_l)
        self.assertEqual(pad_r, 'padl([RequestId], 9)')

        pad_c = self.test_text_col.pad_str(9, 'center')
        self.assertEqual(pad_r, 'padc([RequestId], 9)')
        test_prefix_insertion(self, self.appreq, pad_c)

    def test_str_filter(self):

        str_filter = self.test_text_col.str_filter('0123456789')
        self.assertEqual(str_filter, "strfilter([RequestId], '0123456789')")
        test_prefix_insertion(self, self.appreq, str_filter)

    def test_char_index(self):

        char_index_0 = self.test_text_col.index('lu')
        test_prefix_insertion(self, self.appreq, char_index_0)
        self.assertEqual(char_index_0.get_sql(), "charindex('lu', [RequestId], 0)")

        char_index_2 = self.test_text_col.index('lu', 2)
        test_prefix_insertion(self, self.appreq, char_index_2)
        self.assertEqual(char_index_2.get_sql(), "charindex('lu', [RequestId], 2)")

    def test_python_str_method_analogues(self):

        # starts with
        starts = self.test_text_col.startswith('test', case_sensitive=True)
        self.assertEqual(starts.get_sql(), "[RequestId] GLOB 'test*'")
        starts = self.test_text_col.startswith('test', case_sensitive=False)
        self.assertEqual(starts.get_sql(), "[RequestId] LIKE 'test%'")

        # Ends with
        ends = self.test_text_col.endswith('test', case_sensitive=True)
        self.assertEqual(ends.get_sql(), "[RequestId] GLOB '*test'")
        ends = self.test_text_col.endswith('test', case_sensitive=False)
        self.assertEqual(ends.get_sql(), "[RequestId] LIKE '%test'")

        # Contains
        contains = self.test_text_col.contains('something', case_sensitive=True)
        self.assertEqual(contains.get_sql(), "[RequestId] GLOB '*something*'")
        contains = self.test_text_col.contains('something', case_sensitive=False)
        self.assertEqual(contains.get_sql(), "[RequestId] LIKE '%something%'")

    def test_trim_method(self):

        trim_string_both = self.test_text_col.trim('test_trim')
        test_prefix_insertion(self, self.appreq, trim_string_both)
        trim_wspace_both = self.test_text_col.trim()
        test_prefix_insertion(self, self.appreq, trim_wspace_both)

        trim_string_right = self.test_text_col.trim('test_trim', 'right')
        test_prefix_insertion(self, self.appreq, trim_string_right)
        trim_wspace_right = self.test_text_col.trim(trim_type='right')
        test_prefix_insertion(self, self.appreq, trim_wspace_right)

        trim_string_left = self.test_text_col.trim('test_trim', 'left')
        test_prefix_insertion(self, self.appreq, trim_string_left)
        trim_wspace_left = self.test_text_col.trim(trim_type='left')
        test_prefix_insertion(self, self.appreq, trim_wspace_left)
