"""
Module with tests for the DRF tools.
"""
from unittest import mock

import pytest
from django.test import TestCase
from requests.exceptions import HTTPError
from requests_mock import Mocker
from rest_framework.exceptions import APIException
from rest_framework.viewsets import ViewSet

from jsm_user_services.drf_tools.permissions import GoogleRecaptchaPermission
from jsm_user_services.drf_tools.permissions import IsUserAllowedToPermission
from jsm_user_services.drf_tools.permissions import RoleBasedPermission
from jsm_user_services.drf_tools.permissions import StatusBasedPermission
from jsm_user_services.exception import IncorrectTypePermissionConfiguration


class TestDRFPermissionClasses(TestCase):
    def setUp(self):
        self.role_based_permission = RoleBasedPermission()
        self.status_based_permission = StatusBasedPermission()
        self.google_permission_recaptcha = GoogleRecaptchaPermission()
        self.allowed_to_based_permission = IsUserAllowedToPermission

    @mock.patch("jsm_user_services.drf_tools.permissions.get_user_data_from_server")
    def test_role_based_permission_should_validate_request_data_and_append_it_to_request(
        self, mocked_get_user_data_from_server
    ):
        request = mock.MagicMock()
        del request.user_data
        append_user_data_to_request = True
        remote_user_data = {"name": "Igor G Peternella", "roles": ["professional"]}

        # get_user_data_from_server answers with an http 200 status
        mocked_get_user_data_from_server.return_value = remote_user_data
        user_data = self.role_based_permission._validate_request_against_user_service(
            request, append_user_data_to_request
        )

        expected_user_data = remote_user_data

        self.assertDictEqual(user_data, expected_user_data)
        self.assertDictEqual(request.user_data, expected_user_data)

    @mock.patch("jsm_user_services.drf_tools.permissions.get_user_data_from_server")
    def test_role_based_permission_should_return_empty_dict_upon_401_from_user_service(
        self, mocked_get_user_data_from_server
    ):
        request = mock.MagicMock()
        del request.user_data
        append_user_data_to_request = True

        # get_user_data_from_server answers with an http 401 status
        error = HTTPError("Unauthorized error!")
        response = mock.MagicMock()
        response.status_code = 401
        setattr(error, "response", response)

        mocked_get_user_data_from_server.side_effect = error

        user_data = self.role_based_permission._validate_request_against_user_service(
            request, append_user_data_to_request
        )

        expected_user_data = {}

        self.assertDictEqual(user_data, expected_user_data)

    @mock.patch("jsm_user_services.drf_tools.permissions.get_user_data_from_server")
    def test_role_based_permission_should_reraise_exception_when_user_service_returns_500(
        self, mocked_get_user_data_from_server
    ):
        request = mock.MagicMock()
        del request.user_data
        append_user_data_to_request = True

        # get_user_data_from_server answers with an http 500 status
        error = HTTPError("A 500 was returned!")
        response = mock.MagicMock()
        response.status_code = 500
        setattr(error, "response", response)

        mocked_get_user_data_from_server.side_effect = error

        with pytest.raises(HTTPError) as e:
            self.role_based_permission._validate_request_against_user_service(request, append_user_data_to_request)
            assert str(e.value) == "A 500 was returned!"

    @mock.patch("jsm_user_services.drf_tools.permissions.get_user_data_from_server")
    def test_permission_shouldnt_call_get_user_data_from_server_when_user_data_is_already_appended_to_request(
        self, mocked_get_user_data_from_server
    ):
        request = mock.MagicMock()
        remote_user_data = {"name": "Remote User", "roles": ["professional"]}
        request.user_data = remote_user_data

        user_data = self.role_based_permission._validate_request_against_user_service(request)

        self.assertDictEqual(user_data, remote_user_data)
        mocked_get_user_data_from_server.assert_not_called()

    @mock.patch("jsm_user_services.drf_tools.permissions.RoleBasedPermission._validate_request_against_user_service")
    def test_validate_user_role_should_return_false_if_user_data_is_an_empty_dict(
        self, mocked___validate_request_against_user_service
    ):
        request = mock.MagicMock()
        mocked___validate_request_against_user_service.return_value = {}

        permission_rslt = self.role_based_permission._validate_user_role(request, allowed_roles=["professional"])
        self.assertFalse(permission_rslt)

    @mock.patch("jsm_user_services.drf_tools.permissions.RoleBasedPermission._validate_request_against_user_service")
    def test_validate_user_role_should_return_false_if_user_data_has_disallowed_role(
        self, mocked___validate_request_against_user_service
    ):
        request = mock.MagicMock()
        mocked___validate_request_against_user_service.return_value = {
            "roles": ["owner"]  # only 'professional' role is allowed
        }

        permission_rslt = self.role_based_permission._validate_user_role(request, allowed_roles=["professional"])
        self.assertFalse(permission_rslt)

    @mock.patch("jsm_user_services.drf_tools.permissions.RoleBasedPermission._validate_request_against_user_service")
    def test_validate_user_role_should_return_true_if_user_data_has_allowed_role(
        self, mocked___validate_request_against_user_service
    ):
        request = mock.MagicMock()
        mocked___validate_request_against_user_service.return_value = {
            "roles": ["professional"]  # only 'professional' role is allowed
        }

        permission_rslt = self.role_based_permission._validate_user_role(request, allowed_roles=["professional"])
        self.assertTrue(permission_rslt)

    @mock.patch("jsm_user_services.drf_tools.permissions.RoleBasedPermission._validate_request_against_user_service")
    def test_validate_user_role_should_return_true_if_user_data_has_allowed_role_when_more_than_one_role_is_allowed(
        self, mocked___validate_request_against_user_service
    ):
        request = mock.MagicMock()
        mocked___validate_request_against_user_service.return_value = {
            "roles": ["manager"]  # only 'manager' and 'employee' roles are allowed
        }

        permission_rslt = self.role_based_permission._validate_user_role(request, allowed_roles=["employee", "manager"])
        self.assertTrue(permission_rslt)

    @mock.patch("jsm_user_services.drf_tools.permissions.StatusBasedPermission._validate_request_against_user_service")
    def test_validate_user_status_should_return_true_if_user_data_has_allowed_status(
        self, mocked___validate_request_against_user_service
    ):
        request = mock.MagicMock()
        mocked___validate_request_against_user_service.return_value = {
            "status": "active"
        }  # only 'active' status is allowed
        permission_rslt = self.status_based_permission._validate_user_status(request, allowed_status=["active"])
        self.assertTrue(permission_rslt)

    @mock.patch("jsm_user_services.drf_tools.permissions.StatusBasedPermission._validate_request_against_user_service")
    def test_validate_user_status_should_return_true_if_user_data_has_allowed_status_when_more_than_one_status_is_allowed(
        self, mocked___validate_request_against_user_service
    ):
        request = mock.MagicMock()
        mocked___validate_request_against_user_service.return_value = {
            "status": "pending-validation"
        }  # only 'active' and 'pending-validation' status are allowed

        permission_rslt = self.status_based_permission._validate_user_status(
            request, allowed_status=["active", "pending-validation"]
        )
        self.assertTrue(permission_rslt)

    @mock.patch("jsm_user_services.drf_tools.permissions.StatusBasedPermission._validate_request_against_user_service")
    def test_validate_user_status_should_return_false_if_user_data_has_disallowed_status(
        self, mocked___validate_request_against_user_service
    ):
        request = mock.MagicMock()
        mocked___validate_request_against_user_service.return_value = {
            "status": "blocked"
        }  # only pending-validation' status is allowed

        permission_rslt = self.status_based_permission._validate_user_status(
            request, allowed_status=["pending-validation"]
        )
        self.assertFalse(permission_rslt)

    @mock.patch("jsm_user_services.drf_tools.permissions.StatusBasedPermission._validate_request_against_user_service")
    def test_validate_user_status_should_return_false_if_user_data_is_an_empty_dict(
        self, mocked___validate_request_against_user_service
    ):
        request = mock.MagicMock()
        mocked___validate_request_against_user_service.return_value = {}

        permission_rslt = self.status_based_permission._validate_user_status(request, allowed_status=["active"])
        self.assertFalse(permission_rslt)

    @mock.patch(
        "jsm_user_services.drf_tools.permissions.IsUserAllowedToPermission._validate_request_against_user_service"
    )
    def test_should_return_false_if_user_data_has_redeem_as_not_allowed_to_parameter_and_its_not_permitted(
        self, mocked_validate_request_against_user_service
    ):
        request = mock.MagicMock()
        mocked_validate_request_against_user_service.return_value = {"not_allowed_to": ["redeem"]}

        permission_rslt = self.allowed_to_based_permission(["redeem"]).has_permission(request, None)
        self.assertFalse(permission_rslt)

    @mock.patch(
        "jsm_user_services.drf_tools.permissions.IsUserAllowedToPermission._validate_request_against_user_service"
    )
    def test_should_return_false_if_user_data_full_match_with_not_allowed_to_parameter(
        self, mocked_validate_request_against_user_service
    ):
        request = mock.MagicMock()
        # user not_allowed_to with one parameter
        mocked_validate_request_against_user_service.return_value = {"not_allowed_to": ["redeem"]}
        permission_rslt = self.allowed_to_based_permission(["redeem"], full_match=True).has_permission(request, None)
        self.assertFalse(permission_rslt)

        # user not_allowed_to with two parameters
        mocked_validate_request_against_user_service.return_value = {"not_allowed_to": ["redeem", "indicate"]}
        permission_rslt = self.allowed_to_based_permission(["redeem", "indicate"], full_match=True).has_permission(
            request, None
        )
        self.assertFalse(permission_rslt)

        # user not_allowed_to with three parameters
        mocked_validate_request_against_user_service.return_value = {"not_allowed_to": ["score", "indicate", "redeem"]}
        permission_rslt = self.allowed_to_based_permission(["redeem", "indicate"], full_match=True).has_permission(
            request, None
        )
        self.assertFalse(permission_rslt)

        mocked_validate_request_against_user_service.return_value = {"not_allowed_to": ["redeem", "indicate", "score"]}
        permission_rslt = self.allowed_to_based_permission(
            ["redeem", "indicate", "score"], full_match=True
        ).has_permission(request, None)
        self.assertFalse(permission_rslt)

    @mock.patch(
        "jsm_user_services.drf_tools.permissions.IsUserAllowedToPermission._validate_request_against_user_service"
    )
    def test_should_return_true_if_user_data_do_not_full_match_with_not_allowed_to_parameter(
        self, mocked_validate_request_against_user_service
    ):
        request = mock.MagicMock()
        mocked_validate_request_against_user_service.return_value = {"not_allowed_to": ["redeem"]}
        permission_rslt = self.allowed_to_based_permission(["redeem", "indicate"], full_match=True).has_permission(
            request, None
        )
        self.assertTrue(permission_rslt)

        mocked_validate_request_against_user_service.return_value = {"not_allowed_to": ["redeem", "score"]}
        permission_rslt = self.allowed_to_based_permission(["redeem", "indicate"], full_match=True).has_permission(
            request, None
        )
        self.assertTrue(permission_rslt)

        mocked_validate_request_against_user_service.return_value = {"not_allowed_to": ["redeem", "indicate"]}
        permission_rslt = self.allowed_to_based_permission(
            ["redeem", "indicate", "score"], full_match=True
        ).has_permission(request, None)
        self.assertTrue(permission_rslt)

    @mock.patch(
        "jsm_user_services.drf_tools.permissions.IsUserAllowedToPermission._validate_request_against_user_service"
    )
    def test_should_raise_exception_if_class_parameter_not_allowed_to_do_not_be_a_list(
        self, mocked_validate_request_against_user_service
    ):
        request = mock.MagicMock()
        mocked_validate_request_against_user_service.return_value = {"not_allowed_to": ["redeem"]}

        with self.assertRaises(IncorrectTypePermissionConfiguration) as context:
            self.allowed_to_based_permission("redeem").has_permission(request, None)
        self.assertTrue("Expected type 'List[str]', got" in context.exception.args[0])

    @mock.patch(
        "jsm_user_services.drf_tools.permissions.IsUserAllowedToPermission._validate_request_against_user_service"
    )
    def test_should_return_false_if_user_data_has_at_list_one_not_allowed_to_parameter(
        self, mocked_validate_request_against_user_service
    ):
        request = mock.MagicMock()
        mocked_validate_request_against_user_service.return_value = {"not_allowed_to": ["redeem"]}

        # full match default equals to False

        permission_rslt = self.allowed_to_based_permission(["redeem", "indication"]).has_permission(request, None)
        self.assertFalse(permission_rslt)

        permission_rslt = self.allowed_to_based_permission(["indication", "redeem"]).has_permission(request, None)
        self.assertFalse(permission_rslt)

        permission_rslt = self.allowed_to_based_permission(["indication", "redeem", "score"]).has_permission(
            request, None
        )
        self.assertFalse(permission_rslt)

        permission_rslt = self.allowed_to_based_permission(["score", "indication", "redeem"]).has_permission(
            request, None
        )
        self.assertFalse(permission_rslt)

    @mock.patch(
        "jsm_user_services.drf_tools.permissions.IsUserAllowedToPermission._validate_request_against_user_service"
    )
    def test_should_return_true_if_user_data_has_redeem_as_not_allowed_to_parameter_but_there_is_no_restriction(
        self, mocked_validate_request_against_user_service
    ):
        request = mock.MagicMock()
        mocked_validate_request_against_user_service.return_value = {"not_allowed_to": ["redeem"]}

        # full match default equals to False
        permission_rslt = self.allowed_to_based_permission(["indication", "score"]).has_permission(request, None)
        self.assertTrue(permission_rslt)

        permission_rslt = self.allowed_to_based_permission(["redee", "score", "indication"]).has_permission(
            request, None
        )
        self.assertTrue(permission_rslt)

    @mock.patch(
        "jsm_user_services.drf_tools.permissions.IsUserAllowedToPermission._validate_request_against_user_service"
    )
    def test_should_return_true_if_user_data_is_empty_or_do_not_return_not_allowed_to_parameter(
        self, mocked_validate_request_against_user_service
    ):
        request = mock.MagicMock()
        mocked_validate_request_against_user_service.return_value = {}
        permission_rslt = self.allowed_to_based_permission(["redeem"]).has_permission(request, None)
        self.assertTrue(permission_rslt)

        mocked_validate_request_against_user_service.return_value = {"not_allowed_to": []}
        permission_rslt = self.allowed_to_based_permission(["redeem"]).has_permission(request, None)
        self.assertTrue(permission_rslt)

        mocked_validate_request_against_user_service.return_value = {"another_parameter": ["redeem"]}
        permission_rslt = self.allowed_to_based_permission(["redeem"]).has_permission(request, None)
        self.assertTrue(permission_rslt)

    @mock.patch("jsm_user_services.drf_tools.permissions.perform_recaptcha_validation")
    def test_should_perform_a_request_to_google_if_captcha_key_is_on_request(self, mocked_google_service):

        request = mock.MagicMock()
        request.headers = {}
        # since the key is on the body, the request to google should be made
        request.data = {"g_recaptcha_response": "some cool value"}

        self.google_permission_recaptcha.has_permission(request, None)

        assert mocked_google_service.called

    @mock.patch("jsm_user_services.drf_tools.permissions.perform_recaptcha_validation")
    def test_should_not_perform_a_request_to_google_if_captcha_key_is_not_on_request(self, mocked_google_service):

        request = mock.MagicMock()

        # since there's no g_recaptcha_response key in both header and body, it shouldn't perform the request to google
        request.headers = {}
        request.data = {}

        self.google_permission_recaptcha.has_permission(request, None)

        assert not mocked_google_service.called

    @mock.patch("jsm_user_services.drf_tools.permissions.perform_recaptcha_validation")
    def test_should_raise_if_key_is_not_on_request_but_exception_is_defined(self, mocked_google_service):
        class TestException(APIException):
            pass

        # noinspection PyTypeChecker
        google_permission_with_another_exception = GoogleRecaptchaPermission(TestException())

        request = mock.MagicMock()

        # since there's no g_recaptcha_response key in both header and body, it shouldn't perform the request to google
        request.headers = {}
        request.data = {}

        with pytest.raises(TestException):
            google_permission_with_another_exception.has_permission(request, None)

        assert not mocked_google_service.called

    @mock.patch("jsm_user_services.drf_tools.permissions.perform_recaptcha_validation")
    def test_should_override_header_key_if_the_same_key_is_present_on_body_too(self, mocked_google_service):

        recaptcha_value_on_body = "some value that will be used"
        request = mock.MagicMock()
        # since the priority is the body data and the key is present on both header and body, the header
        # should be ignored
        request.headers = {"g-recaptcha-response": "some value that will be ignored :("}
        request.data = {"g-recaptcha-response": recaptcha_value_on_body}

        self.google_permission_recaptcha.has_permission(request, None)

        mocked_google_service.assert_called_once_with(recaptcha_value_on_body)

    @mock.patch("jsm_user_services.drf_tools.permissions.perform_recaptcha_validation")
    def test_should_get_the_underscore_key_instead_of_dash_if_both_keys_are_present(self, mocked_google_service):

        recaptcha_value_on_key_with_underscore = "some value that will be used"
        request = mock.MagicMock()
        request.headers = {}
        # since the priority is the underscore (g_recaptcha_response) key and both underscore (g_recaptcha_response) and
        # dash(g-recaptcha-response) are present, the dash key should be ignored
        request.data = {
            "g-recaptcha-response": "some value that will be ignored :(",
            "g_recaptcha_response": recaptcha_value_on_key_with_underscore,
        }

        self.google_permission_recaptcha.has_permission(request, None)

        mocked_google_service.assert_called_once_with(recaptcha_value_on_key_with_underscore)

    def test_permission_class_should_succeed_if_google_verification_succeeded(self):

        request = mock.MagicMock()
        request.headers = {}
        request.data = {
            "g_recaptcha_response": "some cool value",
        }

        with Mocker(real_http=True) as mocker:
            mocked_request = mocker.post(
                "https://www.google.com/recaptcha/api/siteverify",
                status_code=200,
                json={"success": True, "score": 0.8},
            )

            assert self.google_permission_recaptcha.has_permission(request, None)
            assert mocked_request.called

    def test_permission_class_should_fail_if_google_verification_failed(self):

        request = mock.MagicMock()
        request.headers = {}
        request.data = {
            "g_recaptcha_response": "some cool value",
        }

        with Mocker(real_http=True) as mocker:
            mocked_request = mocker.post(
                "https://www.google.com/recaptcha/api/siteverify",
                status_code=200,
                json={"success": False},
            )

            assert not self.google_permission_recaptcha.has_permission(request, None)
            assert mocked_request.called

    def test_permission_class_should_raise_if_google_verification_failed_and_api_exception_is_initialized(self):
        class TestException(APIException):
            pass

        google_permission_with_api_exception = GoogleRecaptchaPermission(TestException())

        request = mock.MagicMock()
        request.headers = {}
        request.data = {
            "g_recaptcha_response": "some cool value",
        }

        with Mocker(real_http=True) as mocker:
            with pytest.raises(TestException):
                mocked_request = mocker.post(
                    "https://www.google.com/recaptcha/api/siteverify",
                    status_code=200,
                    json={"success": False},
                )

                google_permission_with_api_exception.has_permission(request, None)
            assert mocked_request.called

    def test_permission_class_should_raise_if_google_verification_failed_and_api_exception_is_not_initialized(self):
        class TestException(APIException):
            pass

        google_permission_with_api_exception = GoogleRecaptchaPermission(TestException)

        request = mock.MagicMock()
        request.headers = {}
        request.data = {
            "g_recaptcha_response": "some cool value",
        }

        with Mocker(real_http=True) as mocker:
            with pytest.raises(TestException):
                mocked_request = mocker.post(
                    "https://www.google.com/recaptcha/api/siteverify",
                    status_code=200,
                    json={"success": False},
                )

                google_permission_with_api_exception.has_permission(request, None)
            assert mocked_request.called

    def test_permission_class_should_not_raise_if_google_verification_failed_and_non_api_exception_is_initialized(self):
        class TestException(Exception):
            pass

        # noinspection PyTypeChecker
        google_permission_with_another_exception = GoogleRecaptchaPermission(TestException())

        request = mock.MagicMock()
        request.headers = {}
        request.data = {
            "g_recaptcha_response": "some cool value",
        }

        with Mocker(real_http=True) as mocker:
            mocked_request = mocker.post(
                "https://www.google.com/recaptcha/api/siteverify",
                status_code=200,
                json={"success": False},
            )

            assert not google_permission_with_another_exception.has_permission(request, None)
            assert mocked_request.called

    def test_permission_class_should_not_raise_if_google_verification_failed_and_non_api_exception_is_not_initialized(
        self,
    ):
        class TestException(Exception):
            pass

        # noinspection PyTypeChecker
        google_permission_with_another_exception = GoogleRecaptchaPermission(TestException)

        request = mock.MagicMock()
        request.headers = {}
        request.data = {
            "g_recaptcha_response": "some cool value",
        }

        with Mocker(real_http=True) as mocker:
            mocked_request = mocker.post(
                "https://www.google.com/recaptcha/api/siteverify",
                status_code=200,
                json={"success": False},
            )

            assert not google_permission_with_another_exception.has_permission(request, None)
            assert mocked_request.called

    def test_should_allow_use_google_permission_initialized(self):
        permission = GoogleRecaptchaPermission()

        class FakeViewSet(ViewSet):

            permission_classes = [permission]

        fake_view_set = FakeViewSet()
        assert fake_view_set.get_permissions() == [permission]

    def test_should_allow_use_allowed_to_permission_initialized(self):
        permission = IsUserAllowedToPermission(["redeem", "score"], full_match=False)

        class FakeViewSet(ViewSet):

            permission_classes = [permission]

        fake_view_set = FakeViewSet()
        assert fake_view_set.get_permissions() == [permission]

    def test_permission_class_should_fail_if_google_verification_score_is_less_than_default(self):

        request = mock.MagicMock()
        request.headers = {}
        request.data = {
            "g_recaptcha_response": "some cool value",
        }

        with Mocker(real_http=True) as mocker:
            mocked_request = mocker.post(
                "https://www.google.com/recaptcha/api/siteverify",
                status_code=200,
                json={"success": True, "score": 0.7},
            )

            assert self.google_permission_recaptcha.has_permission(request, None) is False
            assert mocked_request.called
