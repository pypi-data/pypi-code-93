from typing import Tuple

import pytest
from flask import jsonify
from flask import request
from flask import Response

ITEM = {
    'uuid': '789d995f-3aa0-4bf8-a37b-2f2f2086d503',
    'name': 'test_item',
    'description': 'Item from tests.',
}


def test_specification__create_item(fx_app, fx_client):
    @fx_app.specification
    def create_item() -> Tuple:
        obj = {**request.json, 'uuid': ITEM['uuid']}
        return jsonify(obj), 201

    r_get = fx_client.post(
        '/items', json={'name': ITEM['name'], 'description': ITEM['description']}
    )
    assert r_get.status_code == 201
    assert r_get.json['uuid'] == ITEM['uuid']
    assert r_get.json['name'] == ITEM['name']
    assert r_get.json['description'] == ITEM['description']


def test_specification__items_list(fx_app, fx_client):
    @fx_app.specification
    def items_list() -> Response:
        return jsonify([ITEM])

    r_get = fx_client.get('/items')
    assert r_get.status_code == 200
    assert r_get.json[0]
    assert r_get.json[0]['uuid'] == ITEM['uuid']
    assert r_get.json[0]['name'] == ITEM['name']
    assert r_get.json[0]['description'] == ITEM['description']


def test_specification__args(fx_app, fx_client):
    @fx_app.specification
    def items_args() -> dict:
        return {
            'page': request.args['page'],
            'per_page': request.args['per_page'],
            'page_list': request.args['page_list'],
        }

    args = {'page': 1, 'per_page': 10, 'page_list': ['first', 'second']}
    r_get = fx_client.get('/items_args', query_string=args)
    assert r_get.status_code == 200
    assert r_get.json == args


def test_specification__add_route_with_path_parameters(fx_app, fx_client):
    @fx_app.specification
    def get_item(uuid: str) -> Response:
        item = {**ITEM, **{'uuid': uuid}}
        return jsonify(item)

    item_uuid = '789d995f-3aa0-4bf8-a37b-2f2f2086d504'
    r_get = fx_client.get(f'/items/{item_uuid}')
    assert r_get.status_code == 200
    assert r_get.json['uuid'] == item_uuid


@pytest.mark.parametrize('path_param', ('BAD_UUID_FORMAT', 1, 1.2, None))
def test_specification__bad_uuid_from_path_params(fx_app, fx_client, path_param):
    @fx_app.specification
    def get_item(uuid: str) -> Response:
        item = {**ITEM, **{'uuid': uuid}}
        return jsonify(item)

    r_get = fx_client.get(f'/items/{path_param}')
    assert r_get.status_code == 400
    assert r_get.json['description'] == "{'uuid': ['Not a valid UUID.']}"


def test_specification__all_type_url_parameters(fx_app, fx_client):
    @fx_app.specification
    def get_path_params(path_str: str, path_int: int, path_float: float) -> Response:
        assert isinstance(path_str, str)
        assert isinstance(path_int, int)
        assert isinstance(path_float, float)

        item = {'path_str': path_str, 'path_int': path_int, 'path_float': path_float}
        return jsonify(item)

    path_params = {'path_str': 'test_str', 'path_int': 2, 'path_float': 2.3}
    r_get = fx_client.get(
        f'/get_path_params/{path_params["path_str"]}/{path_params["path_int"]}/{path_params["path_float"]}'  # noqa: E501
    )
    assert r_get.status_code == 200
    assert r_get.json['path_str'] == path_params['path_str']
    assert r_get.json['path_int'] == path_params['path_int']
    assert r_get.json['path_float'] == path_params['path_float']


def test_specification__multiple_routes(fx_app, fx_client):
    @fx_app.specification
    def first() -> dict:
        return {'message': 'OK'}

    @fx_app.specification
    def second() -> dict:
        return {'message': 'OK'}

    assert fx_client.get('/first').status_code == 200
    assert fx_client.get('/second').status_code == 200
