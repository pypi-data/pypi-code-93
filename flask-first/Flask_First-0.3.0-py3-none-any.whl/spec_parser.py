"""The module contains tools for preprocessing and serializing the OpenAPI specification."""
from copy import deepcopy

from openapi_spec_validator import validate_spec
from yaml import CLoader as Loader
from yaml import load

from .schemas import OpenAPIObjectSchema


class Specification:
    """This class implemented methods for specification API."""

    def __init__(self, path_to_spec: str):
        self.raw_spec = self._load_from_yaml(path_to_spec)
        self._move_parameters_to_method()
        self.spec = self._serialization_spec()
        self.routes = self._get_routes()

    @staticmethod
    def _load_from_yaml(spec_path: str) -> dict:
        with open(spec_path) as spec_file:
            spec = load(spec_file, Loader=Loader)
        validate_spec(deepcopy(spec))
        return spec

    def _move_parameters_to_method(self):
        """Move section with common parameters from route to method."""
        for _, methods in self.raw_spec["paths"].items():
            common_parameters = methods.pop('parameters', None)
            if common_parameters:
                for _, fields in methods.items():
                    method_parameters = fields.get('parameters')
                    if method_parameters:
                        fields['parameters'].extend(common_parameters)
                    else:
                        fields['parameters'] = common_parameters

    def _serialization_spec(self):
        schema = OpenAPIObjectSchema()
        schema.context['raw_spec'] = self.raw_spec
        return schema.load(self.raw_spec)

    def _get_routes(self) -> dict:
        routes = {}
        for route, methods in self.spec['paths'].items():
            for method, operation in methods.items():
                routes.update({operation['operationId']: {'route': route, 'method': method}})
                if operation.get('parameters'):
                    routes[operation['operationId']].update({'parameters': operation['parameters']})

        return routes
