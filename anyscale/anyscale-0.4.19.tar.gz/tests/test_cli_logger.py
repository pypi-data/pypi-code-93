from contextlib import redirect_stderr, redirect_stdout
import io
import os
from unittest.mock import Mock, patch

import click
import pytest

from anyscale.api import get_anyscale_api_client, get_api_client
from anyscale.cli_logger import _CliLogger
from anyscale.client.openapi_client.rest import ApiException as ApiExceptionInternal
from anyscale.sdk.anyscale_client.rest import ApiException as ApiExceptionExternal


def test_warning_to_stderr():
    # Test warnings are printed to stderr
    log = _CliLogger()
    f = io.StringIO()
    warning_message = "test_warning"
    with redirect_stderr(f):
        log.warning(warning_message)

    assert warning_message in f.getvalue()


def test_debug_env_var():
    log = _CliLogger()
    f = io.StringIO()
    debug_message = "test_debug"

    # Test debug message is not printed to stdout if ANYSCALE_DEBUG != 1
    os.environ.pop("ANYSCALE_DEBUG", None)
    with redirect_stdout(f):
        log.debug(debug_message)
    assert f.getvalue() == ""

    # Test debug message is printed to stdout if ANYSCALE_DEBUG == 1
    os.environ["ANYSCALE_DEBUG"] = "1"
    with redirect_stdout(f):
        log.debug(debug_message)
    assert debug_message in f.getvalue()


def test_format_api_exception_internal():
    # Tests that API exceptions are correctly formatted for the internal API
    _CliLogger()
    with patch.multiple(
        "anyscale.api", load_credentials=Mock(return_value="fake_credentials")
    ):
        mock_api_client = get_api_client()

    # Test non ApiExceptions are not caught by log.format_api_exception
    with patch.multiple(
        "anyscale.api.openapi_client.ApiClient",
        call_api=Mock(side_effect=ZeroDivisionError()),
    ), pytest.raises(ZeroDivisionError):
        mock_api_client.get_project_api_v2_projects_project_id_get("bad_project_id")

    e = ApiExceptionInternal()
    e.headers = Mock(_container={})
    with patch.multiple(
        "anyscale.api.openapi_client.ApiClient", call_api=Mock(side_effect=e),
    ):
        # Test original ApiException is raised if ANYSCALE_DEBUG == 1
        os.environ["ANYSCALE_DEBUG"] = "1"
        with pytest.raises(ApiExceptionInternal):
            mock_api_client.get_project_api_v2_projects_project_id_get("bad_project_id")

        # Test formatted ClickException is raised if ANYSCALE_DEBUG != 1
        os.environ.pop("ANYSCALE_DEBUG", None)
        with pytest.raises(click.ClickException):
            mock_api_client.get_project_api_v2_projects_project_id_get("bad_project_id")


def test_format_api_exception_external():
    # Tests that API exceptions are correctly formatted for the external API
    _CliLogger()
    with patch.multiple(
        "anyscale.api", load_credentials=Mock(return_value="fake_credentials")
    ):
        mock_api_client = get_anyscale_api_client()

    # Test non ApiExceptions are not caught by log.format_api_exception
    with patch.multiple(
        "anyscale.sdk.anyscale_client.ApiClient",
        call_api=Mock(side_effect=ZeroDivisionError()),
    ), pytest.raises(ZeroDivisionError):
        mock_api_client.list_projects()

    e = ApiExceptionExternal()
    e.headers = Mock(_container={})
    with patch.multiple(
        "anyscale.sdk.anyscale_client.ApiClient", call_api=Mock(side_effect=e),
    ):
        # Test original ApiException is raised if ANYSCALE_DEBUG == 1
        os.environ["ANYSCALE_DEBUG"] = "1"
        with pytest.raises(ApiExceptionExternal):
            mock_api_client.list_projects()

        # Test formatted ClickException is raised if ANYSCALE_DEBUG != 1
        os.environ.pop("ANYSCALE_DEBUG", None)
        with pytest.raises(click.ClickException):
            mock_api_client.list_projects()
