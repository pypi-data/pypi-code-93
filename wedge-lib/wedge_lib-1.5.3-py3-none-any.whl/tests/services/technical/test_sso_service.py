import pytest
from django.conf import settings
from django.test.utils import override_settings
from rest_framework.exceptions import AuthenticationFailed

from w.services.technical.models.sso import SsoValidToken
from w.services.technical.sso_service import SsoService
from w.tests.helpers import sso_test_helper
from w.tests.mixins.testcase_mixin import TestCaseMixin


class TestSsoService(TestCaseMixin):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.user_data = {
            "email": "user@email.com",
            "username": "user@email.com",
            "first_name": "user-firstname",
            "last_name": "user-lastname",
            "password": "user-pwd",
            "client_roles": {"app1": ["role_app1"]},
        }

    def setup_method(self):
        SsoService.clear()
        SsoService.init()
        with sso_test_helper.mock_keycloak_admin_init() as m:
            SsoService._init_keycloak_admin()
        self.keycloak_admin = m

    """
    is_token_valid
    """

    def test_token_is_valid_with_not_initialize_service_raise_runtime_error(self):
        """Ensure method raise RuntimeError if service is not initialized"""
        SsoService.clear()
        match = "Service SsoService must be initialized first"
        with pytest.raises(RuntimeError, match=match):
            SsoService.is_token_valid("need-to-be-initialized")

    def test_token_is_valid_with_invalid_token_raise_error(self):
        """Ensure method raise AuthenticationFailed if token is invalid"""
        match = "Invalid or expired token."
        with sso_test_helper.valid_token_failure():
            with pytest.raises(AuthenticationFailed, match=match):
                SsoService.is_token_valid("invalid-token")

    def test_token_is_valid_with_success_return_sso_token(self):
        """Ensure method succeed"""
        with sso_test_helper.sso_introspect_success() as m:
            actual = SsoService.is_token_valid("valid-token")
        assert isinstance(actual, SsoValidToken)
        self.assert_equals_resultset(
            {"actual": actual.to_dict(), "mock_calls": self.get_mock_calls(m)}
        )

    """
    get_clients
    """

    def test_get_clients_with_not_init_service_raise_error(self):
        """Ensure method raise RuntimeError if not initialized"""
        SsoService.clear()
        match = "Service SsoService must be initialized first"
        with pytest.raises(RuntimeError, match=match):
            SsoService.get_clients()

    def test_get_clients_with_missing_admin_raise_error(self):
        """Ensure method raise RuntimeError if not initialized"""
        SsoService.clear()
        sso_settings = {**settings.SSO}
        sso_settings.pop("ADMIN_PASSWORD")
        SsoService.init()

        match = "Missing SSO settings ADMIN_LOGIN or ADMIN_PASSWORD"
        with override_settings(SSO=sso_settings):
            with pytest.raises(RuntimeError, match=match):
                SsoService.get_clients()

    def test_get_clients_with_success_return_dict(self):
        """Ensure method succeeds"""
        self.keycloak_admin.get_clients.return_value = self.get_dataset(
            "sso/get_clients_success.json"
        )
        actual = SsoService.get_clients()
        self.assert_equals_resultset(actual)

    """
    get_client_roles
    """

    def test_get_client_roles_with_success_return_dict(self):
        """Ensure method succeed"""
        self.keycloak_admin.get_client_roles.return_value = self.get_dataset(
            "sso/get_client_roles.json"
        )
        actual = SsoService.get_client_roles("client-id")
        self.assert_equals_resultset(
            {"actual": actual, "mocks": self.get_mock_calls(self.keycloak_admin)}
        )

    """
    get_or_create_user
    """

    def test_get_or_create_user_with_unknown_user_return_user(self):
        """Ensure method create user in sso server if not exist"""
        self.keycloak_admin.get_user_id.return_value = None
        self.keycloak_admin.create_user.return_value = "user-id"
        self.keycloak_admin.get_clients.return_value = self.get_dataset(
            "sso/get_clients_success.json"
        )
        self.keycloak_admin.get_client_roles.return_value = self.get_dataset(
            "sso/get_client_roles.json"
        )
        self.keycloak_admin.assign_client_role.return_value = None
        self.keycloak_admin.get_user.return_value = self.get_dataset(
            "sso/get_user_success.json"
        )
        actual = SsoService.get_or_create_user(self.user_data)
        self.assert_equals_resultset(
            {"actual": actual, "mocks": self.get_mock_calls(self.keycloak_admin)}
        )
        self.save_as_dataset(
            "sso_service/get_or_create_user_with_unknown_user_return_user.json", actual
        )

    def test_get_or_create_user_with_known_user_return_user(self):
        """Ensure method only retrieve user in sso server if exist"""
        self.keycloak_admin.get_user_id.return_value = "user-id"
        self.keycloak_admin.get_user.return_value = self.get_dataset(
            "sso/get_user_success.json"
        )
        actual = SsoService.get_or_create_user(self.user_data)
        self.assert_equals_resultset(
            {"actual": actual, "mocks": self.get_mock_calls(self.keycloak_admin)}
        )

    """
    require_update_password
    """

    def test_require_update_password_with_known_user_return_none(self):
        """Ensure method returns None if user exists"""
        self.keycloak_admin.send_update_account.return_value = None
        actual = SsoService.require_update_password(
            self.user_data["username"], client_id="my_client"
        )
        self.assert_equals_resultset(
            {"actual": actual, "mocks": self.get_mock_calls(self.keycloak_admin)}
        )
