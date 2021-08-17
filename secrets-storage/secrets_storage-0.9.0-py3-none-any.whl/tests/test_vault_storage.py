import pytest

from secrets_storage import Secrets, VaultStorage


class TestVaultStorage:
    def test_if_not_found_client_token(self, tmpdir, requests_mock):
        mock_token_file = tmpdir.mkdir("serviceaccount").join("token")
        mock_token_file.write("token")

        requests_mock.register_uri(
            method="POST",
            url="http://test.env/v1/auth/kubernetes/login",
            status_code=200,
            text='{"auth": {"client_token": null}}',
        )

        with pytest.raises(ValueError):
            VaultStorage(
                host="http://test.env",
                namespace="TEST_NS",
                role="TEST_ROLE",
                auth_token_path=str(mock_token_file),
            )

    def test_if_not_available(self):
        vault_storage = VaultStorage(
            host="http://test.env",
            namespace="TEST_NS",
            role="TEST_ROLE",
            auth_token_path="test",
            available=False,
        )

        secrets = Secrets(storages=[vault_storage])
        with pytest.raises(ValueError):
            secrets.get("DEMO")

    def test_success_kv1(self, tmpdir, requests_mock):
        mock_token_file = tmpdir.mkdir("serviceaccount").join("token")
        mock_token_file.write("token")

        requests_mock.register_uri(
            method="POST",
            url="http://test.env/v1/auth/kubernetes/login",
            status_code=200,
            text='{"auth": {"client_token": "TEST_CLIENT_TOKEN"}}',
        )
        requests_mock.register_uri(
            method="GET",
            url="http://test.env/v1/TEST_NS",
            status_code=200,
            text='{"data": {"DEMO": "Test"}}',
        )

        vault_storage = VaultStorage(
            host="http://test.env",
            namespace="TEST_NS",
            role="TEST_ROLE",
            auth_token_path=str(mock_token_file),
            kv_version="v1",
        )

        secrets = Secrets(storages=[vault_storage])
        assert secrets.get("DEMO") == "Test"

    def test_success_kv2(self, tmpdir, requests_mock):
        mock_token_file = tmpdir.mkdir("serviceaccount").join("token")
        mock_token_file.write("token")

        requests_mock.register_uri(
            method="POST",
            url="http://test.env/v1/auth/kubernetes/login",
            status_code=200,
            text='{"auth": {"client_token": "TEST_CLIENT_TOKEN"}}',
        )
        requests_mock.register_uri(
            method="GET",
            url="http://test.env/v1/TEST_NS",
            status_code=200,
            text='{"data": {"data": {"DEMO": "Test"}}}',
        )

        vault_storage = VaultStorage(
            host="http://test.env",
            namespace="TEST_NS",
            role="TEST_ROLE",
            auth_token_path=str(mock_token_file),
            kv_version="v2",
        )

        secrets = Secrets(storages=[vault_storage])
        assert secrets.get("DEMO") == "Test"

    def test_not_valid_kv_version(self, tmpdir, requests_mock):
        mock_token_file = tmpdir.mkdir("serviceaccount").join("token")
        mock_token_file.write("token")

        requests_mock.register_uri(
            method="POST",
            url="http://test.env/v1/auth/kubernetes/login",
            status_code=200,
            text='{"auth": {"client_token": "TEST_CLIENT_TOKEN"}}',
        )
        requests_mock.register_uri(
            method="GET",
            url="http://test.env/v1/TEST_NS",
            status_code=200,
            text='{"data": {"data": {"DEMO": "Test"}}}',
        )

        with pytest.raises(ValueError):
            VaultStorage(
                host="http://test.env",
                namespace="TEST_NS",
                role="TEST_ROLE",
                auth_token_path=str(mock_token_file),
                kv_version="fail",
            )

    def test_if_not_found(self, tmpdir, requests_mock):
        mock_token_file = tmpdir.mkdir("serviceaccount").join("token")
        mock_token_file.write("token")

        requests_mock.register_uri(
            method="POST",
            url="http://test.env/v1/auth/kubernetes/login",
            status_code=200,
            text='{"auth": {"client_token": "TEST_CLIENT_TOKEN"}}',
        )
        requests_mock.register_uri(
            method="GET",
            url="http://test.env/v1/TEST_NS",
            status_code=200,
            text="{}",
        )

        vault_storage = VaultStorage(
            host="http://test.env",
            namespace="TEST_NS",
            role="TEST_ROLE",
            auth_token_path=str(mock_token_file),
        )

        secrets = Secrets(storages=[vault_storage])
        with pytest.raises(ValueError):
            secrets.get("DEMO")

    def test_if_not_found_with_fallback_value(self, tmpdir, requests_mock):
        mock_token_file = tmpdir.mkdir("serviceaccount").join("token")
        mock_token_file.write("token")

        requests_mock.register_uri(
            method="POST",
            url="http://test.env/v1/auth/kubernetes/login",
            status_code=200,
            text='{"auth": {"client_token": "TEST_CLIENT_TOKEN"}}',
        )
        requests_mock.register_uri(
            method="GET",
            url="http://test.env/v1/TEST_NS",
            status_code=200,
            text="{}",
        )

        vault_storage = VaultStorage(
            host="http://test.env",
            namespace="TEST_NS",
            role="TEST_ROLE",
            auth_token_path=str(mock_token_file),
        )

        secrets = Secrets(storages=[vault_storage])
        assert secrets.get("DEMO", "Test") == "Test"
