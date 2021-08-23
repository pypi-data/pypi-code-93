from unittest.mock import Mock

from django.test import TestCase
from jsm_user_services.middleware import JsmJwtService
from jsm_user_services.services.user import get_session_id_from_bearer_token
from jsm_user_services.support.local_threading_utils import get_from_local_threading
from jsm_user_services.support.string_utils import get_first_value_from_comma_separated_string


def _build_mocked_request(user_ip: str) -> Mock:
    request = Mock()
    request.META = {
        "REQUEST_METHOD": "POST",
        "HTTP_X_ORIGINAL_FORWARDED_FOR": user_ip,
        "HTTP_AUTHORIZATION": "Bearer abc",
    }
    request.path = "/fake/url/"
    request.session = {}
    return request


class TestMiddleware(TestCase):
    def setUp(self):
        self.user_ip = "8.8.8.8"
        self.user_ip_comma_separated = "7.7.7.7, 8.8.8.8, 9.9.9.9"

        self.middleware = JsmJwtService()

        self.request = _build_mocked_request(self.user_ip)
        self.request_comma_separated_user_ip = _build_mocked_request(self.user_ip_comma_separated)

    def test_should_get_user_ip_from_request(self):
        response = self.middleware.process_request(self.request)
        self.assertIsNone(response)

        self.assertEqual(get_from_local_threading("user_ip"), self.user_ip)

    def test_should_get_user_ip_from_request_when_an_ip_list_is_given(self):
        expected_user_ip = get_first_value_from_comma_separated_string(self.user_ip_comma_separated)
        self.assertEqual(expected_user_ip, "7.7.7.7")

        response = self.middleware.process_request(self.request_comma_separated_user_ip)
        self.assertIsNone(response)
        self.assertEqual(get_from_local_threading("user_ip"), expected_user_ip)

    def test_should_get_user_session_id_from_request(self):
        response, expected_session_id = (
            self.middleware.process_request(self.request),
            get_session_id_from_bearer_token("abc"),
        )

        self.assertIsNone(response)
        self.assertEqual(get_from_local_threading("user_session_id"), expected_session_id)

    def test_should_retrieve_user_session_id_as_none_when_request_is_made_without_bearer_token(self):
        del self.request.META["HTTP_AUTHORIZATION"]
        self.middleware.process_request(self.request)

        self.assertIsNone(get_from_local_threading("user_session_id"))

        self.request.META["HTTP_AUTHORIZATION"] = "Token abc"
        self.middleware.process_request(self.request)

        self.assertIsNone(get_from_local_threading("user_session_id"))

    def test_should_replace_user_session_id_after_request_made_with_bearer_token(self):
        self.middleware.process_request(self.request)

        self.assertIsNotNone(get_from_local_threading("user_session_id"))

        del self.request.META["HTTP_AUTHORIZATION"]
        self.middleware.process_request(self.request)

        self.assertIsNone(get_from_local_threading("user_session_id"))

    def test_should_replace_authorization_token_after_request_made_with_bearer_token(self):
        self.middleware.process_request(self.request)

        self.assertIsNotNone(get_from_local_threading("authorization_token"))

        del self.request.META["HTTP_AUTHORIZATION"]
        self.middleware.process_request(self.request)

        self.assertIsNone(get_from_local_threading("authorization_token"))

    def test_should_replace_user_ip_after_request_made_with_expected_ip_header(self):
        self.middleware.process_request(self.request)

        self.assertIsNotNone(get_from_local_threading("authorization_token"))

        del self.request.META["HTTP_X_ORIGINAL_FORWARDED_FOR"]
        self.middleware.process_request(self.request)

        self.assertIsNone(get_from_local_threading("user_ip"))
