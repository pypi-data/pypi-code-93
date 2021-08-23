import json

import httpretty
import pytest

from jsm_user_services.exception import EmailValidationError
from jsm_user_services.services.everest import perform_email_validation
from jsm_user_services.support.email_utils import perform_callback_function_validators
from jsm_user_services.support.email_utils import validate_format_email
from jsm_user_services.support.settings_utils import get_from_settings_or_raise_missing_config

EVEREST_API_URL = get_from_settings_or_raise_missing_config(
    "EVEREST_API_HOST", "https://api.everest.validity.com/api/2.0/validation/addresses"
)


class TestValidateEmail:

    invalid_emails = [
        "ayron.araujo",
        "loiraojuntossomosmais.io",
        "leydsonjuntossomosmais.lol",
        "aldojuntossomosmais.com.br",
        "ayron41.@gmail.com",
        "emailqualquer@@juntossomosmais.com.br",
        "???@outlook.com",
        "",
    ]

    valid_emails = [
        "ayron41@gmail.com",
        "ayron.araujo@juntossomosmais.com.br",
        "ayron.style@hotmail.com",
    ]

    @pytest.mark.parametrize("email", invalid_emails)
    def test_should_return_false_when_email_is_invalid(self, email: str):

        assert perform_callback_function_validators([validate_format_email], email) is False

    @pytest.mark.parametrize("email", valid_emails)
    def test_should_return_true_when_email_is_valid(self, email: str):

        assert perform_callback_function_validators([validate_format_email], email) is True


class TestValidateEmailRequest:

    @httpretty.activate
    def test_should_return_false_when_email_is_invalid_and_everest_response_is_400(self):

        mocked_response = {"status": "Bad Request: Invalid email address."}
        email: str = "a!dod&sist*ndo@juntossomosmais.com.br"
        url: str = f"{EVEREST_API_URL}/{email}"
        httpretty.register_uri(
            httpretty.GET, url, responses=[httpretty.Response(body=json.dumps(mocked_response), status=400)]
        )
        assert perform_email_validation(email).get("is_valid") is False

    @httpretty.activate
    def test_should_return_false_if_email_is_invalid_response_is_400_use_callback_is_false(self):

        with pytest.raises(EmailValidationError):
            mocked_response = {"status": "Bad Request: Invalid email address."}
            email: str = "a!dod&sist*ndo@juntossomosmais.com.br"
            url: str = f"{EVEREST_API_URL}/{email}"
            httpretty.register_uri(
                httpretty.GET, url, responses=[httpretty.Response(body=json.dumps(mocked_response), status=400)]
            )
            assert perform_email_validation(email, False)

    @httpretty.activate
    def test_should_return_true_when_email_is_valid_and_everest_response_is_200(self):

        mocked_response = {
            "meta": {},
            "results": {
                "category": "valid",
                "status": "valid",
                "name": "Valid",
                "definition": "The email has a valid account associated with it.",
                "reasons": [],
                "risk": "low",
                "recommendation": "send",
                "address": "ayron41@gmail.com",
                "diagnostics": {"role_address": False, "disposable": False, "typo": False},
            },
        }
        email: str = "ayron41@gmail.com"
        url: str = f"{EVEREST_API_URL}/{email}"
        httpretty.register_uri(
            httpretty.GET, url, responses=[httpretty.Response(body=json.dumps(mocked_response), status=200)]
        )
        assert perform_email_validation(email).get("is_valid") is True

    @httpretty.activate
    def test_should_return_false_when_email_is_invalid_and_everest_response_is_200(self):

        mocked_response = {
            "meta": {},
            "results": {
                "category": "email_domain_invalid",
                "status": "invalid",
                "name": "Domain Invalid",
                "reasons": [],
                "risk": "very_high",
                "recommendation": "suppress",
                "address": "ayron41@gmail.com.br",
                "diagnostics": {"role_address": False, "disposable": False, "typo": False},
            },
        }
        email: str = "ayron41@gmail.com.br"
        url: str = f"{EVEREST_API_URL}/{email}"
        httpretty.register_uri(
            httpretty.GET, url, responses=[httpretty.Response(body=json.dumps(mocked_response), status=200)]
        )
        assert perform_email_validation(email).get("is_valid") is False

    @httpretty.activate
    def test_should_return_false_when_email_is_invalid_and_everest_response_is_200_and_empty(self):

        mocked_response = {}
        email: str = "ayron41@gmail.com"
        url: str = f"{EVEREST_API_URL}/{email}"
        httpretty.register_uri(
            httpretty.GET, url, responses=[httpretty.Response(body=json.dumps(mocked_response), status=200)]
        )
        assert perform_email_validation(email).get("is_valid") is False

    @httpretty.activate
    def test_should_retry_request_when_status_code_returned_is_504(self):

        email: str = "ayron.araujo@juntossomosmais.com.br"
        url: str = f"{EVEREST_API_URL}/{email}"
        mocked_error_response = {"status": "Gateway Timeout"}
        mocked_response = {"results": {"status": "risky"}}
        error_timeout_httpretty = httpretty.Response(body=json.dumps(mocked_error_response), status=504)
        success_response_httpretty = httpretty.Response(body=json.dumps(mocked_response), status=200)
        httpretty.register_uri(
            httpretty.GET,
            url,
            responses=[
                error_timeout_httpretty,
                error_timeout_httpretty,
                error_timeout_httpretty,
                success_response_httpretty,
            ],
        )
        assert perform_email_validation(email).get("is_valid") is True

    @httpretty.activate
    def test_should_return_false_when_email_is_invalid_and_everest_response_is_500(self):

        email: str = "a!dod&sist*ndo@juntossomosmais.com.br"
        url: str = f"{EVEREST_API_URL}/{email}"
        mocked_error_response = {"status": "Error!"}
        error_httpretty = httpretty.Response(body=json.dumps(mocked_error_response), status=500)
        httpretty.register_uri(httpretty.GET, url, responses=[error_httpretty])
        assert perform_email_validation(email).get("is_valid") is False
