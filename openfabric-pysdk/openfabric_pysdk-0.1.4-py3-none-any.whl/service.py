from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask, session
from flask_apispec import FlaskApiSpec
from flask_restful import Api

from openfabric_pysdk.api import OpenfabricRestApi
from openfabric_pysdk.manifest import manifest
from openfabric_pysdk.socket import OpenfabricSocket


class OpenfabricService:
    __app: Flask = None
    __api: Api = None
    __docs: FlaskApiSpec = None
    __socket: OpenfabricSocket = None

    def __init__(self, app: Flask):
        self.__app = app
        self.__install_specs()
        self.__api = Api(app)
        self.__docs = FlaskApiSpec(app)

    def __install_specs(self):
        specs = {
            'APISPEC_SPEC': APISpec(
                title=manifest.get('name'),
                version=manifest.get('version'),
                plugins=[MarshmallowPlugin()],
                openapi_version='2.0.0',
                info=dict(
                    termsOfService='https://openfabric.ai/terms/',
                    contact=dict(name=manifest.get('organization'), url="https://openfabric.ai"),
                    description=manifest.get('description')),
            ),
            'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
            'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
        }
        self.__app.config.update(specs)

    def install_rest(self, endpoint):
        print(f"Install APP REST endpoints on {endpoint}")
        self.__api.add_resource(OpenfabricRestApi, endpoint)
        self.__docs.register(OpenfabricRestApi)

    def install_socket(self, endpoint):
        print(f"Install APP SOCKET endpoints on {endpoint}")
        self.__socket = OpenfabricSocket(endpoint, session, self.__app)

    def run(self, debug, host):
        self.__app.run(debug=debug, host=host)
