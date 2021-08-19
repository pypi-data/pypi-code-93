import flask
import serpyco
import rapidjson
from abc import abstractmethod
from typing import List, Dict, Any, Optional

from .context import Context
from .flask import FlaskContext
from .endpoints import Endpoint
from .guards import EndpointGuard, bouncer
from .responses import HttpError, BadRequest


# -- Request data ------------------------------------------------------------

class RequestDataProvider(object):
    """
    Provides request parameters.
    """
    @abstractmethod
    def get(self) -> Optional[Dict[str, Any]]:
        raise NotImplementedError


class JsonBodyProvider(RequestDataProvider):
    """
    Reads request data from request body JSON.
    """
    def get(self) -> Optional[Dict[str, Any]]:
        if not flask.request.data:
            return None

        try:
            return rapidjson.loads(flask.request.data.decode('utf8'))
        except rapidjson.JSONDecodeError:
            raise BadRequest('Invalid JSON body provided')


class QueryStringProvider(RequestDataProvider):
    """
    Reads request data from query parameters.
    """
    def get(self) -> Optional[Dict[str, Any]]:
        return dict(flask.request.args)


# -- Orchestrator ------------------------------------------------------------


class RequestOrchestrator(object):
    """
    Orchestrates handling of HTTP requests on behalf of an endpoint.

    Behaves as a Flask endpoint, ie. it is callable without taking any
    parameters, so it plugs into Flask seamlessly.
    """
    def __init__(
            self,
            endpoint: Endpoint,
            data: RequestDataProvider,
            guards: List[EndpointGuard] = None,
    ):
        self.endpoint = endpoint
        self.data = data
        self.guards = guards

    def __call__(self) -> flask.Response:
        """
        Invoked by Flask to handle a HTTP request.
        """
        try:
            return self.invoke_endpoint()
        except HttpError as e:
            return self.handle_http_error(e)
        except Exception as e:
            raise
            return self.handle_exception(e)

    def build_context(self) -> Context:
        """
        Creates a new request context.
        """
        return FlaskContext()

    def invoke_endpoint(self) -> flask.Response:
        """
        TODO
        """
        context = self.build_context()

        if self.guards:
            bouncer.validate(context, self.guards)

        # kwargs passed to Endpoint.handle_request()
        handler_kwargs = {}

        if self.endpoint.requires_context:
            handler_kwargs['context'] = context

        # Deserialize request data (if necessary)
        if self.endpoint.should_parse_request_data:
            # Defaulting to an empty dictionary makes it possible to omit
            # request data for models where all fields are optional
            handler_kwargs['request'] = self.parse_request_data(self.data.get() or {})

        # Invoke endpoint
        response_body = self.endpoint.handle_request(**handler_kwargs)

        # Serialize response object (if necessary)
        if self.endpoint.should_parse_response_object:
            response_body = self.parse_response_object(response_body)
            response_mimetype = 'application/json'
        else:
            # TODO
            response_body = ''
            response_mimetype = 'text/html'

        return flask.Response(
            status=200,
            mimetype=response_mimetype,
            response=response_body,
        )

    def handle_http_error(self, e: HttpError) -> flask.Response:
        """
        TODO
        """
        return flask.Response(
            response=e.msg,
            status=e.status_code,
            mimetype='text/html',
        )

    def handle_exception(self, e: Exception) -> flask.Response:
        """
        TODO
        """
        return flask.Response(
            response='Internal Server Error',
            status=500,
            mimetype='text/html',
        )

    def parse_request_data(self, data: Dict[str, Any]) -> Any:
        """
        TODO
        """
        try:
            return self.endpoint.request_serializer.load(data, True)
        except serpyco.exception.ValidationError as e:
            # JSON schema validation failed for request data
            # TODO Parse ValidationError to something useful
            raise BadRequest(str(e))

    def parse_response_object(self, response: Any) -> str:
        """
        TODO
        """
        return self.endpoint.response_serializer.dump_json(response)
