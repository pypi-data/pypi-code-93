import unittest
import lumipy as lm
import datetime as dt
import pandas as pd

from test.test_utils import load_secrets_into_env_if_local_run


class TestFinbourneInternalQueries(unittest.TestCase):

    """Integration tests for FINBOURNE-internal use cases using internal data providers.

    """

    def setUp(self) -> None:
        load_secrets_into_env_if_local_run()
        self.atlas = lm.get_atlas()

    def test_atlas_build(self):

        providers = self.atlas.list_providers()
        self.assertGreater(len(providers), 0)

    def test_small_apprequest_log_query(self):

        # Small test query
        appreq = self.atlas.lusid_logs_apprequest(
            start_at=dt.datetime(2021, 2, 1),
            end_at=dt.datetime(2021, 2, 2)
        )
        qry = appreq.select('*').limit(100)

        df = qry.go()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape[0], 100)
        self.assertEqual(df.shape[1], len(qry.get_columns()))

    def test_table_variable_query(self):

        # Performance analysis test case

        appreq = self.atlas.lusid_logs_apprequest(
            start_at=dt.datetime(2021, 2, 1),
            end_at=dt.datetime(2021, 2, 2)
        )
        test_table_var = appreq.select(
            appreq.method,
            appreq.application,
            ApiSeconds=appreq.duration*0.001
        ).limit(100).to_table_var('test_table_var')

        qry = test_table_var.select('*')

        df = qry.go()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape[0], 100)
        self.assertEqual(df.shape[1], 3)
        expected = {'Method', 'Application', 'ApiSeconds'}
        self.assertEqual(set(df.columns), expected)

    def test_cost_explorer_join(self):

        # Test case for cost monitoring

        ce_feb = self.atlas.sys_aws_billing_costanduse(
            start_at=dt.datetime(2021, 2, 1),
            end_at=dt.datetime(2021, 3, 1),
            dimension1='service',
            dimension2='usage_type'
        )
        ce_mar = self.atlas.sys_aws_billing_costanduse(
            start_at=dt.datetime(2021, 3, 1),
            end_at=dt.datetime(2021, 4, 1),
            dimension1='service',
            dimension2='usage_type'
        )

        feb = ce_feb.select(
            ce_feb.dimension1_value,
            ce_feb.dimension2_value
        ).group_by(
            ce_feb.dimension1_value, ce_feb.dimension2_value
        ).aggregate(
            TotalSpend=ce_feb.blended_cost.sum()
        ).to_table_var('february')

        mar = ce_mar.select(
            ce_mar.dimension1_value,
            ce_mar.dimension2_value
        ).group_by(
            ce_mar.dimension1_value,
            ce_mar.dimension2_value
        ).aggregate(
            TotalSpend=ce_mar.blended_cost.sum()
        ).to_table_var('march')

        qry = feb.inner_join(
            mar,
            on=(feb.dimension1_value == mar.dimension1_value) & (feb.dimension2_value == mar.dimension2_value)
        ).select(
            Service=mar.dimension1_value,
            UsageType=mar.dimension2_value,
            SpendChange=mar.total_spend - feb.total_spend
        ).order_by(
            (mar.total_spend - feb.total_spend).descending()
        )

        df = qry.go()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape[0], 578)
        self.assertEqual(df.shape[1], 3)

    def test_long_running_api_calls_rtrace_join_query(self):

        # Test case for rtrace brakdown of long-running api calls
        rtrace = self.atlas.lusid_logs_requesttrace()
        appreq = self.atlas.lusid_logs_apprequest(
            start_at=dt.datetime(2021, 2, 1),
            end_at=dt.datetime(2021, 2, 2)
        )

        test_table_var = appreq.select(
            appreq.method,
            appreq.request_id,
            ApiSeconds=appreq.duration*0.001
        ).where(
            (appreq.duration > 10000) &
            (appreq.event_type == 'Completed')
        ).limit(10).to_table_var('test_table_var')

        qry = test_table_var.inner_join(
            rtrace,
            on=rtrace.request_id == test_table_var.request_id
        ).select(
            rtrace.function_name
        ).where(
            (rtrace.self_time > 0)
        ).group_by(
            rtrace.function_name
        ).aggregate(
            SelfTimeSum=rtrace.self_time.sum()
        ).order_by(
            rtrace.self_time.sum().descending()
        )

        df = qry.go()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape[0], 76)
        self.assertEqual(df.shape[1], 2)

    def test_large_query_get_result_pagination_bug(self):

        appreq = self.atlas.lusid_logs_apprequest()
        qry = appreq.select('*').limit(11000)

        df = qry.go(fetch_page_size=10000)
        self.assertEqual(11000, df.shape[0])
