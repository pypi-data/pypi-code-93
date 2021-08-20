# coding: utf8

__all__ = ["Endpoint"]

import asyncio
import logging
import urllib.parse
from enum import Enum, unique
from json import JSONDecodeError

import requests

from refinitiv.dataplatform.tools._common import urljoin, get_response_reason
from refinitiv.dataplatform.errors import EndpointError
from refinitiv.dataplatform.legacy import get_default_session


class Endpoint(object):
    @unique
    class RequestMethod(Enum):
        """
        The RESTful Data service can support multiple methods when sending requests to a specified endpoint.
           GET : Request data from the specified endpoint.
           POST : Send data to the specified endpoint to create/update a resource.
           DELETE : Request to delete a resource from a specified endpoint.
           PUT : Send data to the specified endpoint to create/update a resource.
        """

        GET = 1
        POST = 2
        DELETE = 3
        PUT = 4

    class Params:
        def __init__(
            self, session=None, url=None, on_response=None, service_class=None
        ):
            self._session = session if session is not None else get_default_session()
            self._url = url
            self._on_response_cb = on_response
            self._service_class = service_class

        @property
        def session(self):
            return self._session

        @session.setter
        def session(self, value):
            """
            The Session defines the platform where you want to retrieve your data.
            """
            from refinitiv.dataplatform.core import Session

            if isinstance(value, Session):
                self._session = value
            else:
                raise TypeError(
                    "Endpoint requires a Session that supports data request"
                )
            return self

        @property
        def url(self):
            return self._url

        @url.setter
        def url(self, value):
            """
            The Url presents the address of the endpoint.
            """
            self._url = value
            return self

        @property
        def on_response(self):
            return self._on_response_cb

        @on_response.setter
        def on_response(self, on_response):
            """
            on_response callback will be called once response will be received on request.
            It could be successful or error
            """
            self._on_response_cb = on_response
            return self

    class Request:
        class Params:
            def __init__(
                self,
                method=None,
                header_params={},
                query_params=None,
                path_params=None,
                body_params=None,
            ):
                if method is None:
                    self._method = Endpoint.RequestMethod.GET
                else:
                    self._method = method

                self._header_parameter = header_params

                if query_params is None:
                    self._query_parameters = {}
                else:
                    self._query_parameters = query_params

                if path_params is None:
                    self._path_parameters = []
                else:
                    self._path_parameters = path_params

                self._body_parameter = body_params

            def with_method(self, value):
                """
                Defines the method of the request.
                Valid methods are: RequestMethod.GET, RequestMethod.POST, RequestMethod.PUT and RequestMethod.DELETE.
                """
                if isinstance(value, Endpoint.RequestMethod):
                    self._method = value
                    return self
                else:
                    raise AttributeError("Method must be RequestMethod type")

            def with_header_parameter(self, key, value):
                """
                Set header parameter GET HTTP request
                """
                if isinstance(key, str) and len(key) and len(value):
                    if self._header_parameter.get(key):
                        if isinstance(self._header_parameter[key], list):
                            self._header_parameter[key].append(value)
                        else:
                            self._header_parameter[key] = list(
                                self._header_parameter[key], value
                            )
                    else:
                        self._header_parameter[key] = value
                return self

            def with_query_parameter(self, key, value):
                """
                Set query parameter key=value for REST API in endpoint request url
                """
                self._query_parameters[key] = value
                return self

            def with_path_parameter(self, key, value):
                """
                Set value parameter in endpoint request url at {key} position
                """
                if (
                    isinstance(key, str)
                    and len(str)
                    and isinstance(value, str)
                    and len(value)
                ):
                    self._path_parameters.append((key, value))
                return self

            def with_body_parameter(self, body):
                """
                Set body for endpoint request body
                """
                if self._body_parameter:
                    # merge existing body parameter with body
                    self._body_parameter = {**self._body_parameter, **body}
                else:
                    self._body_parameter = body
                return self

        def __init__(self, params):
            self._parameters = None
            if isinstance(params, Endpoint.Request.Params):
                self._parameters = params
            else:
                raise AttributeError(
                    "Endpoint.Request requires an Endpoint.Request.Params"
                )

    class EndpointData(object):
        def __init__(self, raw):
            self._raw = raw
            self._dataframe = None

        @property
        def raw(self):
            return self._raw

        @property
        def df(self):
            return self._dataframe

    class EndpointResponse(object):
        def __init__(self, response, service_class=None):
            self._service_class = service_class
            self._response = response
            self._request_message = dict()
            self._data = None
            self._status = {}
            self._error_code = None
            self._error_message = None
            self._is_success = False
            _raw = None

            if response is not None:
                self._request_message["headers"] = response.request.headers
                self._request_message["url"] = response.request.url

                self._status = self._http_response_status(response)
                self._is_success = self._response.status_code is requests.codes.ok

                if self.is_success:
                    _media_type = response.headers.get("content-type")
                    if "/json" in _media_type:
                        self._process_response_json(response)
                    elif "text/plain" in _media_type or "text/html" in _media_type:
                        self._process_response_text(response)
                    elif "image/" in _media_type:
                        self._process_response_image(response)
                    elif "text/xml" in _media_type:
                        self._process_response_xml(response)
                    else:
                        self._status = self._http_response_status(response)
                        self._status[
                            "content"
                        ] = f"Unknown media type returned: {_media_type}"
                        if self._service_class:
                            self._data = self._service_class.Data(None)
                        else:
                            self._data = Endpoint.EndpointData(None)
                else:
                    try:
                        _raw = response.json()
                        if _raw and _raw.get("error"):
                            self.status["error"] = _raw["error"]
                            self._error_code = _raw["error"].get("code")
                            self._error_message = _raw["error"].get("message")
                        else:
                            self._error_code = response.status_code
                            self._error_message = response.text
                    except (ValueError, TypeError, JSONDecodeError):
                        self._error_code = response.status_code
                        self._error_message = response.text

                    if self._service_class:
                        self._data = self._service_class.Data(_raw)
                    else:
                        self._data = Endpoint.EndpointData(_raw)

        def _process_response_json(self, response):
            _data = None
            try:
                _json = response.json()
                if _json is None:
                    # Some HTTP responses, such as a DELETE, can be successful without any response body.
                    _data = {}
                else:
                    _data = _json
            except (ValueError, TypeError, JSONDecodeError) as error:
                self._is_success = False
                if hasattr(self, "_params"):
                    self._params._session.log(
                        logging.ERROR, f"Cannot get json from response: {error}"
                    )
                self._status[
                    "content"
                ] = f"Failed to process HTTP response : {str(error)}"
                self._process_response_text(response)

            if self._service_class:
                self._data = self._service_class.Data(_data)
            else:
                self._data = Endpoint.EndpointData(_data)

        def _process_response_text(self, response):
            try:
                if self._service_class:
                    self._data = self._service_class.Data(response.text)
                else:
                    self._data = Endpoint.EndpointData(response.text)
            except Exception as e:
                self._params._session.log(
                    logging.ERROR, f"Cannot get text from response: {e}"
                )
                self._status["content"] = f"Failed to process HTTP response : {str(e)}"
                if self._service_class:
                    self._data = self._service_class.Data(None)
                else:
                    self._data = Endpoint.EndpointData(None)

        def _process_response_image(self, response):
            try:
                self._data = Endpoint.EndpointData(response.text)
            except Exception as e:
                self._params._session.log(
                    logging.ERROR, f"Cannot get image from response: {e}"
                )
                self._status["content"] = f"Failed to process HTTP response : {str(e)}"
                if self._service_class:
                    self._data = self._service_class.Data(None)
                else:
                    self._data = Endpoint.EndpointData(None)

        def _process_response_xml(self, response):
            try:
                if self._service_class:
                    self._data = self._service_class.Data(response.text)
                else:
                    self._data = Endpoint.EndpointData(response.text)
            except Exception as e:
                self._params._session.log(
                    logging.ERROR, f"Cannot get xml from response: {e}"
                )
                self._status["content"] = f"Failed to process HTTP response : {str(e)}"
                if self._service_class:
                    self._data = self._service_class.Data(None)
                else:
                    self._data = Endpoint.EndpointData(None)

        def _http_response_status(self, response):
            return {
                "http_status_code": response.status_code,
                "http_reason": get_response_reason(response),
            }

        @property
        def is_success(self):
            return self._is_success

        @property
        def data(self):
            return self._data

        @property
        def status(self):
            return self._status

        @property
        def error_code(self):
            return self._error_code

        @property
        def error_message(self):
            return self._error_message

        @property
        def http_response(self):
            if self._response is not None:
                return self._response
            return None

        @property
        def headers(self):
            if self._response is not None:
                return self._response.headers
            return None

        @property
        def request_message(self):
            if self._response is not None:
                return self._response.request
            return None

        @property
        def closure(self):
            if self._response is not None:
                _request = self._response.request
                _headers = _request.headers
                return _headers.get("closure")
            return None

    def __init__(self, session, url, on_response=None, service_class=None):
        self._params = Endpoint.Params(session, url, on_response, service_class)

    def __del__(self):
        self._params = None

    @property
    def url(self):
        return self._params.url

    @url.setter
    def url(self, value):
        self._params.url = value

    @property
    def session(self):
        return self._params.session

    ########################################################
    #  methods to select method and prepare url            #
    ########################################################
    @staticmethod
    def _update_url(session, url, path_parameters, query_parameters):
        try:
            result = urllib.parse.urlparse(url)
            if not all([result.scheme, result.netloc, result.path]):
                # url = u'/'.join([session._get_rdp_url_root(), url])
                url = urljoin(session._get_rdp_url_root(), url)
            else:
                url = "".join([session._get_rdp_url_root(), result.path])
        except Exception as e:
            url = "/".join([session._get_rdp_url_root() + "/" + url])

        if path_parameters:
            for key, value in path_parameters.items():
                value = urllib.parse.quote(value)
                url = url.replace("{" + key + "}", value)

        if query_parameters:
            url = "?".join([url, urllib.parse.urlencode(query_parameters)])

        return url

    @staticmethod
    def _define_method(method):
        if method is Endpoint.RequestMethod.POST:
            return "POST"
        elif method is Endpoint.RequestMethod.PUT:
            return "PUT"
        elif method is Endpoint.RequestMethod.DELETE:
            return "DELETE"
        return "GET"

    ########################################################
    #  methods to send asynchronously request to endpoint  #
    ########################################################
    async def send_request_with_params_async(self, request_params=None):
        """
        Send the request with parameters asynchronously to url.
        """
        from refinitiv.dataplatform.core import Session

        if self._params._session is None:
            raise AttributeError("Session is mandatory")

        if self._params._url is None:
            raise AttributeError("url is mandatory")

        if not isinstance(request_params, Endpoint.Request.Params):
            raise AttributeError(
                "request_params must be an instance of Endpoint.Request.Params"
            )

        if self._params._session.get_open_state() == Session.State.Open:
            _method = "GET"
            _url = self._params._url
            _body = None
            _headers = None

            if request_params:
                _method = self._define_method(request_params._method)
                _url = self._update_url(
                    self._params.session,
                    _url,
                    request_params._path_parameters,
                    request_params._query_parameters,
                )
                if _method != "GET":
                    _body = request_params._body_parameter
                    _headers = {"Content-Type": "application/json"}
                    _headers.update(request_params._header_parameter)

            self._params._session.log(
                logging.DEBUG, "Send endpoint request asynchronously"
            )
            self._params._session.log(
                1, "  {} to {}\n   with body {}".format(_method, _url, _body)
            )
            _response = await self._params._session.http_request_async(
                _url,
                method=_method,
                headers=_headers,
                # data=...,
                # params=...,
                json=_body,
            )
            if self._params._service_class:
                _result = self._params._service_class.Response(_response)
            else:
                _result = Endpoint.EndpointResponse(_response)

            if _result.status.get("error"):
                _error = _result.status.get("error")
                self._params._session.log(1, f"Response contains error : {_error}")

            self.on_response(_result)
            return _result

        return None

    async def send_request_async(
        self,
        method=None,
        header_parameters={},
        path_parameters=None,
        query_parameters=None,
        body_parameters=None,
        closure=None,
    ):
        """
        Send the request with parameters asynchronously to url.
        """
        from refinitiv.dataplatform.core import Session

        if self._params.session is None:
            raise AttributeError("Session is mandatory")

        if self._params.url is None:
            raise AttributeError("url is mandatory")

        if self._params.session.get_open_state() == Session.State.Open:
            _method = self._define_method(method)
            _url = self._params.url
            _url = self._update_url(
                self._params.session, _url, path_parameters, query_parameters
            )
            self._params.session.log(
                logging.DEBUG, f"Send {_method} request asynchronously to {_url}"
            )
            _headers = None
            _body = None
            if _method != "GET":
                _body = body_parameters
                _headers = {"Content-Type": "application/json"}
                if header_parameters:
                    _headers.update(header_parameters)
                self._params.session.log(1, f"\theaders : {_headers}\n\tbody : {_body}")

            _response = await self._params.session.http_request_async(
                _url,
                method=_method,
                headers=_headers,
                # data=...,
                # params=...,
                json=_body,
                closure=closure,
            )

            if self._params._service_class:
                _result = self._params._service_class.Response(_response)
            else:
                _result = Endpoint.EndpointResponse(_response)

            self.on_response(_result)
            return _result

        raise EndpointError(-1, "Session is not opened. Can't send any request")

    ######################################################
    #  methods to send synchronously request to endpoint #
    ######################################################
    def send_request_with_params(self, request_params=None):
        """
        Send the request with parameters synchronously to this endpoint.
        """
        self._params.session.log(
            logging.DEBUG, "Send synchronously request to Endpoint"
        )

        _response = self._params.session._loop.run_until_complete(
            self.send_request_with_params_async(request_params)
        )

        return _response

    def send_request(
        self,
        method=None,
        header_parameters={},
        path_parameters=None,
        query_parameters=None,
        body_parameters=None,
        closure=None,
    ):
        """
        Send the request with parameters synchronously to this endpoint.
        """
        self._params.session.log(
            logging.DEBUG, "Send synchronously request to Endpoint {}"
        )

        _response = self._params.session._loop.run_until_complete(
            self.send_request_async(
                method,
                header_parameters,
                path_parameters,
                query_parameters,
                body_parameters,
                closure,
            )
        )

        return _response

    def on_response(self, response):
        if self._params.on_response:
            if asyncio.get_event_loop() == self.session._loop:
                self._params.on_response(self, response)
            else:
                self.session._loop.call_soon_threadsafe(
                    self._params.on_response, self, response
                )
