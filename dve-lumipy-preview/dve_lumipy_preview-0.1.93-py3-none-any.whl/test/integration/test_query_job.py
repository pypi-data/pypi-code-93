import unittest
import lumipy as lm
import datetime as dt
import pandas as pd
import time

from test.test_utils import load_secrets_into_env_if_local_run


class TestQueryJob(unittest.TestCase):

    """Integration tests for async usage of QueryJob class

    """

    def setUp(self) -> None:
        load_secrets_into_env_if_local_run()
        self.atlas = lm.get_atlas()

    def test_query_job_status_progress_and_result(self):

        pf = self.atlas.lusid_portfolio(
            effective_at=dt.datetime(2021, 3, 1),
            as_at=dt.datetime(2021, 3, 8)
        )

        job = pf.select('*').limit(1000).go_async()

        status = job.get_status()
        self.assertNotEqual(status, '')
        while status == 'WaitingForActivation':
            status = job.get_status()
            self.assertNotEqual(status, '')
            time.sleep(1)

        df = job.get_result()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape[0], 1000)

        log = job.get_progress()
        self.assertIsInstance(log, str)
        self.assertGreater(len(log), 0)
