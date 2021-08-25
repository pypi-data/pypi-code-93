import os
from typing import Any

import click

import anyscale.client.openapi_client as openapi_client
from anyscale.client.openapi_client.api.default_api import DefaultApi
from anyscale.client.openapi_client.rest import ApiException as ApiExceptionInternal
import anyscale.conf
from anyscale.credentials import load_credentials
import anyscale.sdk.anyscale_client as anyscale_client
from anyscale.sdk.anyscale_client.api.default_api import DefaultApi as AnyscaleApi
from anyscale.sdk.anyscale_client.rest import ApiException as ApiExceptionExternal
import anyscale.shared_anyscale_utils.conf as shared_anyscale_conf
from anyscale.shared_anyscale_utils.headers import RequestHeaders
from anyscale.version import __version__ as version


def instantiate_api_client(
    no_cli_token: bool = False, cli_token: str = "", host: str = ""
) -> DefaultApi:
    """
    Instantiates client to interact with our frontend APIs
    """
    if (cli_token and not host) or (not cli_token and host):
        raise ValueError("Both cli_token and host need to be provided.")

    if not no_cli_token and anyscale.conf.CLI_TOKEN is None and not cli_token:
        anyscale.conf.CLI_TOKEN = load_credentials()
    configuration = openapi_client.Configuration(
        host=host or shared_anyscale_conf.ANYSCALE_HOST
    )
    configuration.connection_pool_maxsize = 100

    if no_cli_token:
        api_client = ApiClientWrapperInternal(configuration)
    else:
        cookie = (
            f"cli_token={cli_token}"
            if cli_token
            else f"cli_token={anyscale.conf.CLI_TOKEN}"
        )
        api_client = ApiClientWrapperInternal(configuration, cookie=cookie)
    configure_open_api_client_headers(api_client, "CLI")
    api_instance = openapi_client.DefaultApi(api_client)
    return api_instance


def instantiate_anyscale_client() -> AnyscaleApi:
    """
    Instantiates client to interact with our externalized APIs
    """

    if anyscale.conf.CLI_TOKEN is None:
        anyscale.conf.CLI_TOKEN = load_credentials()

    configuration = anyscale_client.Configuration(
        host=shared_anyscale_conf.ANYSCALE_HOST + "/ext"
    )
    configuration.connection_pool_maxsize = 100

    api_client = ApiClientWrapperExternal(
        configuration, cookie=f"cli_token={anyscale.conf.CLI_TOKEN}"
    )
    configure_open_api_client_headers(api_client, "CLI")

    api_instance = anyscale_client.DefaultApi(api_client)
    return api_instance


def get_api_client() -> DefaultApi:
    if _api_client.api_client is None:
        _api_client.api_client = instantiate_api_client()

    return _api_client.api_client


def get_anyscale_api_client() -> AnyscaleApi:
    if _api_client.anyscale_client is None:
        _api_client.anyscale_client = instantiate_anyscale_client()

    return _api_client.anyscale_client


# client is of type APIClient, which is auto-generated
def configure_open_api_client_headers(client: Any, client_name: str) -> None:
    client.set_default_header(RequestHeaders.CLIENT, client_name)
    client.set_default_header(RequestHeaders.CLIENT_VERSION, version)


class _ApiClient(object):
    api_client: DefaultApi = None
    anyscale_client: AnyscaleApi = None


def format_api_exception(e, method: str, resource_path: str) -> None:
    if os.environ.get("ANYSCALE_DEBUG") == "1":
        raise e
    else:
        raise click.ClickException(
            f"API Exception ({e.status}) from {method} {resource_path} \n"
            f"Reason: {e.reason}\nHTTP response body: {e.body}\n"
            f"Trace ID: {e.headers._container.get('x-trace-id', None)}"
        )


class ApiClientWrapperInternal(openapi_client.ApiClient):
    def call_api(
        self,
        resource_path,
        method,
        path_params=None,
        query_params=None,
        header_params=None,
        body=None,
        post_params=None,
        files=None,
        response_type=None,
        auth_settings=None,
        async_req=None,
        _return_http_data_only=None,
        collection_formats=None,
        _preload_content=True,
        _request_timeout=None,
        _host=None,
    ):
        try:
            return openapi_client.ApiClient.call_api(
                self,
                resource_path,
                method,
                path_params,
                query_params,
                header_params,
                body,
                post_params,
                files,
                response_type,
                auth_settings,
                async_req,
                _return_http_data_only,
                collection_formats,
                _preload_content,
                _request_timeout,
                _host,
            )
        except ApiExceptionInternal as e:
            format_api_exception(e, method, resource_path)


class ApiClientWrapperExternal(anyscale_client.ApiClient):
    def call_api(
        self,
        resource_path,
        method,
        path_params=None,
        query_params=None,
        header_params=None,
        body=None,
        post_params=None,
        files=None,
        response_type=None,
        auth_settings=None,
        async_req=None,
        _return_http_data_only=None,
        collection_formats=None,
        _preload_content=True,
        _request_timeout=None,
        _host=None,
    ):
        try:
            return anyscale_client.ApiClient.call_api(
                self,
                resource_path,
                method,
                path_params,
                query_params,
                header_params,
                body,
                post_params,
                files,
                response_type,
                auth_settings,
                async_req,
                _return_http_data_only,
                collection_formats,
                _preload_content,
                _request_timeout,
                _host,
            )
        except ApiExceptionExternal as e:
            format_api_exception(e, method, resource_path)


_api_client = _ApiClient()
