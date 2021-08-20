import re
import json
import yaml
from functools import wraps
from inspect import signature, Parameter

import click
from flask import request, jsonify, abort

from .types import validate, json_schema, Reference, String
from .generation import api_template


class SchemaValidationError(Exception):
    pass


class Operation:
    def __init__(self, operation_id, summary, path, method,
                response_type, parameters, body_type, types):
        self.operation_id = operation_id
        self.path = path
        self.summary = summary
        self.method = method
        self.response_type = response_type
        self.parameters = parameters
        self.body_type = body_type
        self.types = types

    def assert_function_fit(self, func):
        def parameter_fits(p, name, optional):
            if name == p.name and p.kind in [Parameter.POSITIONAL_OR_KEYWORD,
                                                Parameter.KEYWORD_ONLY]:
                return optional or p.default is not Parameter.empty
            elif p.kind == Parameter.VAR_KEYWORD:
                return True
            else:
                return False

        sig = signature(func, follow_wrapped=False)
        for desc in self.parameters:
            assert any(parameter_fits(p, desc['name'], desc['required'])
                                            for p in sig.parameters.values()), \
                f'callable does not handle parameter { desc["name"] }'

    def get_parameters(self, path_params, req):
        kwargs = {}

        for desc in self.parameters:
            if desc['in'] == 'query':
                if desc['name'] in req.args:
                    kwargs[desc['name']] = req.args[desc['name']]
                elif desc['required']:
                    raise SchemaValidationError(f'parameter { desc["name"] } is required')
            elif desc['in'] == 'path':
                kwargs[desc['name']] = path_params[desc['name']]
            else:
                raise Exception("unknown 'in' value")

        if self.body_type:
            errors = list(validate(self.body_type, request.json, self.types))
            if errors:
                raise SchemaValidationError(
                    'Malformed body\n\n%s' % _format_errors(errors))
            kwargs = {"body": request.json, **kwargs}

        return kwargs


class Styx:
    def __init__(self, app, version, prefix=''):
        self.app = app
        self.version = version
        self.prefix = prefix.rstrip('/')

        self.types = {}
        self.operations = []

        @app.cli.command()
        @click.argument('file', type=click.File('w'), default='-')
        def generate_client(file):
            """ Generates a typescript client
            """
            file.write(api_template.render(styx=self))

    def define_type(self, name, type_):
        self.types[name] = type_
        return Reference(name)
        # return type_

    def operation(self, operation_id, *,
                            summary,
                            path,
                            method,
                            response_type,
                            parameters=None,
                            body_type=None):

        assert path.startswith('/')

        self.operations.append(
            Operation(operation_id, summary, self.prefix + path, method,
                        response_type, parameters or [], body_type, self.types))

    def openapi_spec(self, server_url):
        paths = {}

        for op in self.operations:
            methods = paths.setdefault(op.path, {})
            methods[op.method] = item = {
                "operationId": op.operation_id,
                "summary": op.summary,
                "parameters": op.parameters,
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": json_schema(op.response_type)
                            }
                        }
                    }
                }
            }
            if op.body_type:
                item['requestBody'] = {
                    "content": {
                        "application/json": {
                            "schema": json_schema(op.body_type)
                        }
                    }
                }

        return {
            'openapi': '3.0.3',
            'info': {
                'title': 'Example API',
                'version': self.version,
            },
            'servers': [{
                "url": server_url,
                "description": "this server",
            }],
            'components': {
                'schemas': {
                    name: json_schema(value) for name, value in self.types.items()
                }
            },
            'paths': paths
        }

    def register_apispec(self, path="/openapi/"):
        @self.app.route(path)
        def apispec():
            return jsonify(self.openapi_spec(request.base_url))

    def register_handler(self, name=None):
        def decorator(func):
            operation = self._find_operation(name or func.__name__)
            operation.assert_function_fit(func)

            path = re.sub(
                        '[{]([^}]*)[}]',
                        lambda m: f'<string:{ m.groups()[0] }>',
                        operation.path)

            @self.app.route(path, methods=[operation.method.upper()])
            @wraps(func)
            def wrapper(**path_params):
                try:
                    kwargs = operation.get_parameters(path_params, request)
                except SchemaValidationError as exc:
                    self.app.logger.info("request validation failed: %r", exc)
                    abort(400)

                response = func(**kwargs)

                errors = validate(operation.response_type, response, self.types)
                if not errors:
                    return response
                else:
                    raise SchemaValidationError(_format_errors(errors)
                                    + '\n\n' + json.dumps(response))

            return func
        return decorator

    def _find_operation(self, name):
        return next(op
                for op in self.operations
                if op.operation_id == name)

    def get_yaml_spec(self, server_url):
        return yaml.dump(self.openapi_spec(server_url))


def _format_errors(errors):
    return '\n'.join(f'.{ ".".join(repr(p) for p in path) } { msg }'
                    for path, msg in errors)


def query_parameter(name, description, type_=String(), required=False):
    return {
        "name": name,
        "in": "query",
        "description": description,
        "required": required,
        "schema": json_schema(type_),
    }


def path_parameter(name, description, type_=String()):
    return {
        "name": name,
        "in": "path",
        "description": description,
        "required": True,
        "schema": json_schema(type_),
    }
