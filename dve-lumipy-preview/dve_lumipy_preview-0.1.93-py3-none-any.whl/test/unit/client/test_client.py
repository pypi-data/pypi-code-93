import unittest
from unittest.mock import patch
from test.unit.utilities.temp_file_manager import TempFileManager

from lusid.utilities import RefreshingToken

from lumipy.client import Client


class TestClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.sample_base_url = "https://fbn-ci.lusid.com/honeycomb"

    def test_createClient_withSecrets_ClientCreatedWithRefreshingToken(self):
        """
        Ensures that a client can be created successfully via a secrets file
        """

        sample_secrets = {
            "api": {
                "tokenUrl": "sample",
                "username": "sample",
                "password": "sample",
                "clientId": "sample",
                "clientSecret": "sample",
                "apiUrl": "sample",
                "lumiApiUrl": self.sample_base_url
            }
        }

        secrets_file = TempFileManager.create_temp_file(sample_secrets)

        client = Client(secrets_path=secrets_file.name)

        TempFileManager.delete_temp_file(secrets_file)

        self.assertIsInstance(client.token, RefreshingToken)
        self.assertEqual(client.base_url, self.sample_base_url+"/api")

    def test_createClient_withExistingToken_ClientCreatedWithToken(self):
        """
        Ensures that a Client can be created successfully with a provided token
        """

        sample_token = "sample_token"

        with patch.dict('os.environ', {Client.luminesce_base_url_env_variable: self.sample_base_url}, clear=True):
            client = Client(token=sample_token)

        self.assertEqual(client.token, sample_token)
        self.assertEqual(client.base_url, self.sample_base_url+"/api")

    def test_createClient_withoutLumiBaseUrl_RaisesException(self):
        """
        Ensures that without a Lumi Base Url a Client can not be created
        """

        sample_token = "sample_token"

        with patch.dict('os.environ', clear=True):
            with self.assertRaises(ValueError) as valueError:
                Client(token=sample_token)
            self.assertIn("Could not locate luminesce base url", str(valueError.exception))
