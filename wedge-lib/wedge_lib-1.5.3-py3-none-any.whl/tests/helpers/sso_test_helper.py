from contextlib import contextmanager
from pathlib import Path
from unittest.mock import Mock

from w.services.technical.models.sso import SsoValidToken
from w.services.technical.sso_service import SsoService
from w.tests.helpers import service_test_helper
from w.tests.mixins.testcase_mixin import TestCaseMixin


def _get_dataset(relative_dataset):
    current_dir = Path(__file__).parent
    dataset_filename = current_dir.joinpath(
        "../fixtures/datasets", relative_dataset
    ).resolve()
    return TestCaseMixin._get_dataset(dataset_filename.name, dataset_filename)


# noinspection PyProtectedMember
def _sso_instrospect_mock_attrs(dataset="introspect_success"):
    return {
        "service": SsoService,
        "method_name": "_sso_introspect",
        "return_value": _get_dataset(f"sso/{dataset}.json"),
    }


def _mock_get_or_create_user():
    return {
        "service": SsoService,
        "method_name": "get_or_create_user",
        "return_value": _get_dataset(
            "sso_service/create_sso_user_with_success_return_dict.json"
        ),
    }


@contextmanager
def mock_keycloak_admin_init():
    keycloak_admin = Mock()
    mock_keycloak_admin = {
        "service": SsoService,
        "method_name": "_get_keycloak_admin",
        "return_value": keycloak_admin,
    }
    with service_test_helper.mock_service(**mock_keycloak_admin):
        yield keycloak_admin


@contextmanager
def valid_token_failure():
    mock_attrs = _sso_instrospect_mock_attrs("introspect_failure")
    with service_test_helper.mock_service(**mock_attrs) as m:
        yield m


@contextmanager
def sso_introspect_success():
    mock_attrs = _sso_instrospect_mock_attrs()
    with service_test_helper.mock_service(**mock_attrs) as m:
        yield m


@contextmanager
def valid_token_success(uuid="fake-uuid"):
    fake_decoded_token = {
        "sub": uuid,
        "given_name": "fake-sub",
        "family_name": "fake-given_name",
        "username": "fake-family_name@fake-mail.com",
        "email": "fake-username@fake-mail.com",
        "resource_access": {
            "account": {
                "roles": ["manage-account", "manage-account-links", "view-profile"]
            }
        },
    }
    mock_attrs = {
        "service": SsoService,
        "method_name": "is_token_valid",
        "return_value": SsoValidToken(fake_decoded_token),
    }
    with service_test_helper.mock_service(**mock_attrs) as m:
        yield m


@contextmanager
def get_or_create_user_success():
    with service_test_helper.mock_service(**_mock_get_or_create_user()) as m:
        yield m
