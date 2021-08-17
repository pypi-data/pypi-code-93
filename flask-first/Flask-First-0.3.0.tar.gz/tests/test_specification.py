from pathlib import Path

from flask import Flask
from flask_first import First
from flask_first import Specification


def test_specification__load_from_yaml(fx_config):
    spec = Specification(fx_config.PATH_TO_SPEC)
    assert spec
    assert spec.spec["info"]["title"] == "Simple API for testing Flask-First"


def test_specification__config_param(fx_app, fx_client):
    @fx_app.specification
    def bad_response() -> dict:
        return {'message': 'OK', 'non_exist_field': 'BAD'}

    fx_app.debug = 0
    fx_app.testing = 0

    assert fx_client.get('/bad_response').status_code == 500


def test_specification__mini_api():
    app = Flask("testing_app")
    app.config['FIRST_RESPONSE_VALIDATION'] = True
    mini_spec = Path('specs/mini.openapi.yaml')
    First(mini_spec, app)

    @app.specification
    def mini_endpoint() -> dict:
        return {'message': 'OK'}


def test_specification__full_field_openapi():
    app = Flask("testing_app")
    app.config['FIRST_RESPONSE_VALIDATION'] = True
    full_spec = Path('specs/full.openapi.yaml')
    First(full_spec, app)

    @app.specification
    def route_path() -> dict:
        return {'string_field': 'OK'}
