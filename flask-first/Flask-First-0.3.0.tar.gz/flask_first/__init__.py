"""Flask extension for using “specification first” principle."""

__version__ = '0.3.0'

from flask import Flask, Request, Response, abort, request
from werkzeug.datastructures import MultiDict

from .exc import (
    FlaskFirstArgsValidation,
    FlaskFirstException,
    FlaskFirstJSONValidation,
    FlaskFirstPathParameterValidation,
    FlaskFirstResponseValidation,
    FlaskFirstValidation,
    register_errors,
)
from .spec_parser import Specification
from .validators import validate_json, validate_parameters


class First:
    """This class is used to generation routes from OpenAPI specification."""

    def __init__(self, path_to_spec: str, app: Flask = None) -> None:
        self.app = app
        self.path_to_spec = path_to_spec

        if self.app is not None:
            self.init_app(app)

        self.spec = Specification(path_to_spec)

    @staticmethod
    def _make_rule(route_path: str, route_parameters: dict = None) -> str:
        """Converts a route from OpenAPI format to Flask format."""
        if route_parameters:
            route_path = route_path.replace('{', '<').replace('}', '>')
        return route_path

    def _route_registration(self, func) -> None:
        try:
            route = self.spec.routes[func.__name__]
        except KeyError as err:
            raise FlaskFirstException(
                f'Route function <{err}> not found in OpenAPI specification!'
            ) from err

        self.app.add_url_rule(
            self._make_rule(route['route'], route_parameters=route.get('parameters')),
            func.__name__,
            func,
            methods=[route['method'].upper()],
        )

    def _extract_route(self, request: Request) -> str:
        url_rule = request.url_rule
        if url_rule is None:
            abort(404, description='Route not found in OpenAPI specification.')
        return url_rule.rule.replace('<', '{').replace('>', '}')

    def _extract_method(self, request: Request) -> str:
        method = request.method
        if method is None:
            abort(405)
        return method.lower()

    def _args_to_dict(self, args: MultiDict) -> dict:
        rendered_args = {}
        for key, value in args.to_dict(flat=False).items():
            if len(value) == 1:
                rendered_args[key] = value[0]
            if len(value) > 1:
                rendered_args[key] = value
        return rendered_args

    def _validate_path_params(self, request: Request, params: dict) -> None:
        try:
            request.view_args = validate_parameters(request.view_args, params)
        except FlaskFirstValidation as e:
            raise FlaskFirstPathParameterValidation(str(e))

    def _validate_args(self, request: Request, params: dict) -> None:
        args = self._args_to_dict(request.args)
        try:
            request.args = validate_parameters(args, params)
        except FlaskFirstValidation as e:
            raise FlaskFirstArgsValidation(str(e))

    def init_app(self, app: Flask) -> None:
        app.config.setdefault('FIRST_RESPONSE_VALIDATION', False)
        register_errors(app)
        app.specification = self.mapping

        @self.app.before_request
        def add_request_validating() -> None:
            route = self._extract_route(request)
            method = self._extract_method(request)

            try:
                parameters = self.spec.spec['paths'][route][method].get('parameters')
            except KeyError as err:
                raise FlaskFirstException(
                    f'Parameters for route function <{request.endpoint}> not found in OpenAPI specification!'  # noqa: E501
                ) from err

            if request.view_args:
                self._validate_path_params(request, parameters)

            if request.args:
                self._validate_args(request, parameters)

            if request.json:
                schema = self.spec.spec['paths'][route][method]['requestBody']['content'][
                    request.content_type
                ]['schema']
                try:
                    validate_json(request.json, schema)
                except FlaskFirstValidation as e:
                    raise FlaskFirstJSONValidation(str(e))

        if app.config['FIRST_RESPONSE_VALIDATION']:

            @self.app.after_request
            def add_response_validating(response: Response) -> Response:
                route = self._extract_route(request)
                method = self._extract_method(request)

                schema = self.spec.spec['paths'][route][method]['responses'][
                    str(response.status_code)
                ]['content'][response.content_type]['schema']
                try:
                    validate_json(response.json, schema)
                    return response
                except FlaskFirstValidation as e:
                    raise FlaskFirstResponseValidation(str(e))

    def mapping(self, func) -> None:
        self._route_registration(func)
