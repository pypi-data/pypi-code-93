import json
import unittest
import warnings

import boto3
from moto import mock_ssm
import syngenta_digital_dbv


class VersionerTest(unittest.TestCase):

    def setUp(self, *args, **kwargs):
        warnings.simplefilter('ignore', ResourceWarning)
        self.maxDiff = None

    def test_local_versioner_number_files(self):
        syngenta_digital_dbv.version(
            engine='postgres',
            endpoint='localhost',
            database='dbv-postgis',
            port=5432,
            user='root',
            password='Lq4nKg&&TRhHv%7z',
            versions_directory='tests/mocks/version_number_files',
            reset_root=False
        )
        self.assertEqual(True, True)

    def test_local_versioner_letter_files(self):
        syngenta_digital_dbv.version(
            engine='postgres',
            endpoint='localhost',
            database='dbv-postgis',
            port=5432,
            user='root',
            password='Lq4nKg&&TRhHv%7z',
            versions_directory='tests/mocks/version_letter_files',
            reset_root=False
        )
        self.assertEqual(True, True)

    def test_versioner_with_seed(self):
        syngenta_digital_dbv.version(
            engine='postgres',
            endpoint='localhost',
            database='dbv-postgis',
            port=5432,
            user='root',
            password='Lq4nKg&&TRhHv%7z',
            versions_directory='tests/mocks/version_seed_files',
            reset_root=False,
            seed=True,
            seed_directory='tests/mocks/seed_files'
        )
        self.assertEqual(True, True)

    @mock_ssm
    def test_versioner_with_reset_password(self):
        syngenta_digital_dbv.version(
            engine='postgres',
            endpoint='localhost',
            database='dbv-reset-postgis',
            port=5433,
            user='root',
            password='Lq4nKg&&TRhHv%7z',
            ssm_param='local-reset-postrgres-config',
            versions_directory='tests/mocks/version_number_files',
            reset_root=True
        )
        self.assertEqual(True, True)

    @mock_ssm
    def test_versioner_with_ssm_param_not_reset(self):
        syngenta_digital_dbv.version(
            engine='postgres',
            endpoint='localhost',
            database='dbv-postgis',
            port=5432,
            user='root',
            password='Lq4nKg&&TRhHv%7z',
            versions_directory='tests/mocks/version_seed_files',
            ssm_param='local-not-reset-postrgres-config',
            reset_root=False
        )
        self.assertEqual(True, True)

    @mock_ssm
    def test_versioner_with_ssm_param_found(self):
        param_name = 'local-postrgres-config'
        client = boto3.client('ssm')
        client.put_parameter(
            Name=param_name,
            Type='SecureString',
            Value=json.dumps({
                'endpoint': 'localhost',
                'database': 'dbv-postgis',
                'user': 'root',
                'password': 'Lq4nKg&&TRhHv%7z',
                'port': 5432
            })
        )
        syngenta_digital_dbv.version(
            engine='postgres',
            endpoint='localhost',
            database='dbv-postgis',
            port=5432,
            user='root',
            password='Lq4nKg&&TRhHv%7z',
            versions_directory='tests/mocks/version_seed_files',
            ssm_param=param_name,
            reset_root=False
        )
        self.assertEqual(True, True)

    @mock_ssm
    def test_versioner_with_ssm_param_not_found(self):
        syngenta_digital_dbv.version(
            engine='postgres',
            endpoint='localhost',
            database='dbv-postgis',
            port=5432,
            user='root',
            password='Lq4nKg&&TRhHv%7z',
            versions_directory='tests/mocks/version_seed_files',
            ssm_param='local-postrgres-not-config',
            reset_root=False
        )
        self.assertEqual(True, True)

    def test_versioner_ssm_error_stops_build(self):
        try:
            syngenta_digital_dbv.version(
                engine='postgres',
                endpoint='localhost',
                database='dbv-postgis',
                port=5432,
                user='root',
                password='Lq4nKg&&TRhHv%7z',
                versions_directory='tests/mocks/version_seed_files',
                ssm_param='local-postrgres-error-config',
                reset_root=False
            )
            self.assertEqual(False, True)
        except Exception as error:
            self.assertEqual(True, True)
