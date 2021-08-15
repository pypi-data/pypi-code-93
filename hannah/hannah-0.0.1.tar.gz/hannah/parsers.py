class SwaggerParser:

    def __init__(self, spec: dict):
        self.spec = spec

    @property
    def operations(self) -> dict:
        _operations = {}
        for uri, resources in self.spec['paths'].items():
            for method, resource in resources.items():
                op = SwaggerOperation(method, uri, resource)
                _operations.update({op.id: op})
        return _operations


class SwaggerOperation:

    def __init__(self, method: str, uri: str, resource_dict: dict):
        self.method = method
        self.uri = uri
        self.resource_dict = resource_dict

    def get_params(self, type: str):
        return [param['name'] for param in self.resource_dict['parameters'] if param['type'] == type]

    @property
    def id(self) -> str:
        return self.resource_dict.get('operationId')

    @property
    def query_params(self) -> list:
        return self.get_params(type='query')

    @property
    def path_params(self) -> list:
        return self.get_params(type='path')

    @property
    def headers(self) -> list:
        return self.get_params(type='header')

    @property
    def body(self) -> [str, None]:
        try:
            return self.get_params(type='body')[0]
        except IndexError:
            return None
