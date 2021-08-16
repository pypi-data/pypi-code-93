import pytest
from phcli.ph_lmd.model.ph_gateway import PhGateway


@pytest.mark.dependency(depends=['test_ph_lambda.test_ph_lambda_create_s3'])
def test_ph_gateway_create():
    args = {
        "name": "test_ph_gateway_create",
        "rest_api_id": "2t69b7x032",
        "api_template": "s3://ph-platform/2020-08-10/template/python/phcli/lmd/jsonapi-openapi-template.yaml",
        "lambda_name": "test_ph_lambda_create",
        "alias_version": "current",
    }
    assert PhGateway().create(args) != {}


def test_ph_gateway_lists():
    assert PhGateway().lists({}) != {}


def test_ph_gateway_get():
    args = {
        "name": "test_ph_gateway_create",
        "rest_api_id": "2t69b7x032",
    }
    assert PhGateway().get(args) != {}


def test_ph_gateway_update():
    args = {
        "name": "test_ph_gateway_create",
        "rest_api_id": "2t69b7x032",
        "api_template": "s3://ph-platform/2020-08-10/template/python/phcli/lmd/jsonapi-openapi-template.yaml",
        "lambda_name": "test_ph_lambda_create",
        "alias_version": "current",
    }
    assert PhGateway().update(args) != {}


def test_ph_gateway_apply():
    args = {
        "name": "test_ph_gateway_create",
        "rest_api_id": "2t69b7x032",
        "api_template": "s3://ph-platform/2020-08-10/template/python/phcli/lmd/jsonapi-openapi-template.yaml",
        "lambda_name": "test_ph_lambda_create",
        "alias_version": "current",
    }
    assert PhGateway().apply(args) != {}


def test_ph_gateway_delete():
    args = {
        "name": "test_ph_gateway_create",
        "rest_api_id": "2t69b7x032",
    }
    assert PhGateway().delete(args) != {}

