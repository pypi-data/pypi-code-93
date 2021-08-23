import pytest
from flask_log_request_id.ctx_fetcher import MultiContextRequestIdFetcher
from pytest_mock import MockFixture
from request_id_django_log import local_threading

from jsm_user_services.exception import RequestIDModuleNotFound
from jsm_user_services.support.request_id import get_current_request_id_callable
from jsm_user_services.support.request_id import import_module_otherwise_none


@pytest.fixture
def no_flask_request_id_module(mocker: MockFixture):
    def mock_only_if_flask_log_request_id_module(module_to_import: str):
        if module_to_import == "flask_log_request_id":
            return None
        return import_module_otherwise_none(module_to_import)

    mocker.patch(
        "jsm_user_services.support.request_id.import_module_otherwise_none",
        side_effect=mock_only_if_flask_log_request_id_module,
    )


@pytest.fixture
def no_django_request_id_module(mocker: MockFixture):
    def mock_only_if_django_request_id_module(module_to_import: str):
        if module_to_import == "request_id_django_log.request_id":
            return None
        return import_module_otherwise_none(module_to_import)

    mocker.patch(
        "jsm_user_services.support.request_id.import_module_otherwise_none",
        side_effect=mock_only_if_django_request_id_module,
    )


@pytest.fixture
def no_request_id_module_found(mocker: MockFixture):
    mocker.patch("jsm_user_services.support.request_id.import_module_otherwise_none", return_value=None)


def test_should_successfully_retrieve_current_request_id_for_django_app(no_flask_request_id_module: None):
    local_threading.request_id, current_request_id = ("django", get_current_request_id_callable())

    django_request_id = current_request_id()

    assert django_request_id == local_threading.request_id

    del local_threading.request_id


def test_should_succesfully_retrieve_current_request_id_for_flask_app(no_django_request_id_module: None):
    current_request_id = get_current_request_id_callable()

    assert isinstance(current_request_id, MultiContextRequestIdFetcher)


def test_should_raise_exception_when_request_id_module_is_not_found(no_request_id_module_found: None):
    with pytest.raises(RequestIDModuleNotFound):
        get_current_request_id_callable()
