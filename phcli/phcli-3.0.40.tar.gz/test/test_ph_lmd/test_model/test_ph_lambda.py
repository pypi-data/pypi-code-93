import os
import pytest
from phcli.ph_lmd.model.ph_lambda import PhLambda


@pytest.mark.skip("skip")
def test_ph_lambda_package_python():
    args = {
        "runtime": "python",
        "code_path": "./phlmd/",
        "package_name": "test_ph_lambda_package_python.zip",
    }

    PhLambda().package(args)
    assert os.path.exists(args["package_name"])
    os.remove("test_ph_lambda_package_python.zip")


@pytest.mark.skip("skip")
def test_ph_lambda_package_nodejs():
    pass


@pytest.mark.skip(reason='Deprecation')
def test_ph_lambda_create_local():
    args = {
        "name": "test_ph_lambda_create",
        "version": "",
        "runtime": "python3.8,python3.6",
        "lambda_path": "file/ph_lmd/python-lambda-example-code.zip",
        "lambda_handler": "hello_world.app.lambda_handler",
        "lambda_layers": "test_ph_layer_create",
        "lambda_desc": "test_ph_lambda_create_local 单元测试",
        "vpc_config": {
            "SubnetIds": [
                'subnet-0260eab5acd58bc53',
                'subnet-0e3daa88acef9b136',
            ],
            "SecurityGroupIds": [
                'sg-058404c2ad02dcbb9',
                'sg-09f5205a1194149ab'
            ]
        },
        "lambda_timeout": 50,
        "lambda_memory_size": 128,
        "lambda_env": {'TEST': 'test'},
        "lambda_tag": {"language": "python"},
    }
    assert PhLambda().create(args) != {}


def test_ph_lambda_create_s3():
    args = {
        "name": "test_ph_lambda_create",
        "version": "",
        "runtime": "python3.8,python3.6",
        "lambda_path": "s3://ph-platform/2020-08-10/functions/python/test_ph_lambda_create/python-lambda-example-code.zip",
        "lambda_handler": "hello_world.app.lambda_handler",
        "lambda_layers": "test_ph_layer_create",
        "lambda_desc": "test_ph_lambda_create_local 单元测试",
        "vpc_config": {
            "SubnetIds": [
                'subnet-0260eab5acd58bc53',
                'subnet-0e3daa88acef9b136',
            ],
            "SecurityGroupIds": [
                'sg-058404c2ad02dcbb9',
                'sg-09f5205a1194149ab'
            ]
        },
        "lambda_timeout": 50,
        "lambda_memory_size": 128,
        "lambda_env": {'TEST': 'test'},
        "lambda_tag": {"language": "python"},
    }
    assert PhLambda().create(args) != {}


def test_ph_lambda_lists():
    args = {}
    assert PhLambda().lists(args) != {}


def test_ph_lambda_get():
    args = {
        "name": "test_ph_lambda_create",
    }
    assert PhLambda().get(args) != {}


def test_ph_lambda_update():
    args = {
        "name": "test_ph_lambda_create",
        "version": "",
        "runtime": "python3.8,python3.6",
        "lambda_path": "s3://ph-platform/2020-08-10/functions/python/test_ph_lambda_create/python-lambda-example-code.zip",
        "lambda_handler": "hello_world.app.lambda_handler",
        "lambda_layers": "test_ph_layer_create:12",
        "lambda_desc": "test_ph_lambda_create_local 单元测试",
        "vpc_config": {
            "SubnetIds": [
                'subnet-0260eab5acd58bc53',
                'subnet-0e3daa88acef9b136',
            ],
            "SecurityGroupIds": [
                'sg-058404c2ad02dcbb9',
                'sg-09f5205a1194149ab'
            ]
        },
        "lambda_timeout": 55,
        "lambda_memory_size": 149,
        "lambda_env": {'TEST': 'test'},
        "lambda_tag": {"language": "python"},
    }
    assert PhLambda().update(args) != {}


def test_ph_lambda_stop():
    args = {
        "name": "test_ph_lambda_create",
    }
    assert PhLambda().stop(args) != {}


def test_ph_lambda_start():
    args = {
        "name": "test_ph_lambda_create",
    }
    assert PhLambda().start(args) != {}


@pytest.mark.skip(reason='Deprecation')
def test_ph_lambda_delete_local():
    args = {
        "name": "test_ph_lambda_create_local",
    }
    assert PhLambda().delete(args) != {}


@pytest.mark.skip(reason='Used for test_ph_gateway Test')
def test_ph_lambda_delete_s3():
    args = {
        "name": "test_ph_lambda_create",
    }
    assert PhLambda().delete(args) != {}
