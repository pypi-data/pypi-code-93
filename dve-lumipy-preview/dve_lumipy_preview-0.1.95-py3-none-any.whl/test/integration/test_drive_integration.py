import unittest
import lumipy as lm
import pandas as pd
import numpy as np
from lusid_drive.exceptions import ApiException

from test.test_utils import load_secrets_into_env_if_local_run


class TestDriveIntegration(unittest.TestCase):
    """Integration tests for lumipy's drive functionality. Tests direct drive client stuff
    as well as using drive direct providers in lumipy.

    """

    def setUp(self) -> None:
        load_secrets_into_env_if_local_run()
        self.atlas = lm.get_atlas()
        self.drive = lm.get_drive()

    def test_drive_create_delete_folder(self):
        path = '/lumipy-int-tests/test-folder-create/'
        try:
            # Enforce fresh start for test...
            self.drive.delete(path)
        except:
            self.drive.create_folder(path)

        self.drive.create_folder(path + '/test/')
        df = self.drive.list_all("/lumipy-int-tests/test-folder-create/")
        self.assertEqual(df.shape[0], 1)

        self.drive.delete(path + '/test/')
        df = self.drive.list_all("/lumipy-int-tests/test-folder-create/")
        self.assertEqual(df.shape[0], 0)

        self.drive.delete(path)

    def test_upload_and_delete_dataframe(self):
        path = '/lumipy-int-tests/dataframe-test/'
        try:
            # Enforce fresh start for test...
            self.drive.delete(path)
        except:
            self.drive.create_folder(path)

        def make_random_df():
            vals = np.random.randint(0, 10, size=(8, 8))
            cols = list('ABCDEFGH')
            return pd.DataFrame(vals, columns=cols)

        # Make a random dataframe
        df = make_random_df()
        # Upload file
        fname = 'test.csv'
        self.drive.upload(df, path + fname)

        # Check it shows up in search
        list_df = self.drive.list_files(path)
        self.assertEqual(list_df.shape[0], 1)

        # Download it and check it matches
        self.drive.download(path + fname, f'/tmp/test_temp.csv')
        dl_df = pd.read_csv(f'/tmp/test_temp.csv')
        self.assertTrue(df.equals(dl_df))

        # Check trying to upload without overwrite=True throws
        with self.assertRaises(ApiException):
            self.drive.upload(df, path + fname)

        # Make another random dataframe
        df2 = make_random_df()
        # Upload file with overwrite=True
        self.drive.upload(df2, path + fname, overwrite=True)

        # Download it again and check it matches new df
        self.drive.download(path + fname, f'/tmp/test_temp.csv')
        dl_df2 = pd.read_csv(f'/tmp/test_temp.csv')
        self.assertTrue(df2.equals(dl_df2))

        # Delete file
        self.drive.delete(path + fname)
        # Check it's gone
        list_df = self.drive.list_files(path)
        self.assertEqual(list_df.shape[0], 0)

        # Delete test folder to clean up
        self.drive.delete(path)
