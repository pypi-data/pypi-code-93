from copy import deepcopy
import json
import os
import tempfile

import pytest
import responses

from datarobot import TARGET_TYPE
from datarobot._experimental import CustomTrainingBlueprint


@pytest.fixture
def mocked_training_model(mocked_models):
    return mocked_models["data"][0]


@pytest.fixture
def mocked_custom_model_version():
    return {
        "id": "5cf4d3f5f930e26daac18aBB",
        "customModelId": "5cf4d3f5f930e26daac18a1BB",
        "label": "Version 2",
        "description": "ss",
        "versionMinor": 2,
        "versionMajor": 3,
        "isFrozen": True,
        "items": [],
        "created": "2019-09-28T15:19:26.587583Z",
    }


@pytest.fixture
def mocked_environment():
    return {
        "id": "5cf4d3f5f930e26daac18a1a",
        "name": "env1",
        "description": "some description",
        "programmingLanguage": "python",
        "isPublic": True,
        "created": "2019-09-28T15:19:26.587583Z",
        "latestVersion": {
            "id": "5cf4d3f5f930e26daac18a1a",
            "environmentId": "5cf4d3f5f930e26daac18a1xx",
            "label": "Version 1",
            "description": "",
            "buildStatus": "success",
            "created": "2019-09-28T15:19:26.587583Z",
        },
    }


@pytest.fixture
def mocked_blueprints(mocked_training_model, mocked_environment):
    return {
        "count": 2,
        "totalCount": 2,
        "next": None,
        "previous": None,
        "data": [
            {
                "userBlueprintId": "5cf4d3f5f930e26daac18a1a",
                "customModel": {"id": mocked_training_model["id"], "name": "cm"},
                "customModelVersion": {"id": "5cf4d3f5f930e26daac18acv", "label": "cmv"},
                "executionEnvironment": {"id": mocked_environment["id"], "name": "ee"},
                "executionEnvironmentVersion": {"id": "5cf4d3f5f930e26daac18aev", "label": "eev"},
                "training_history": [],
            },
            {
                "userBlueprintId": "5cf4d3f5f930e26daac18a2b",
                "customModel": {"id": "5cf4d3f5f930e26daac18bcc", "name": "cm n2"},
                "customModelVersion": {"id": "5cf4d3f5f930e26daac18bcv", "label": "cmv n2"},
                "executionEnvironment": {"id": "5cf4d3f5f930e26daac18bee", "name": "ee n2"},
                "executionEnvironmentVersion": {
                    "id": "5cf4d3f5f930e26daac18bev",
                    "label": "eev n2",
                },
                "training_history": [
                    {
                        "pid": "5cf4d3f5f930e26daac18abc",
                        "project_name": "my_project",
                        "lid": "5cf4d3f5f930e26daac18bbbe",
                        "creation_date": "2019-09-07T15:50-04:00",
                        "project_models_count": 3,
                        "target_name": "my_target",
                    },
                    {
                        "pid": "5cf4d3f5f930e26daac18abc",
                        "project_name": "my_project",
                        "lid": "5cf4d3f5f930e26daac18cce",
                        "creation_date": "2019-09-07T15:50-06:00",
                        "project_models_count": 3,
                        "target_name": "my_target",
                    },
                ],
            },
        ],
    }


@pytest.fixture
def mocked_blueprint(mocked_blueprints):
    return mocked_blueprints["data"][0]


@pytest.fixture
def make_blueprints_url(unittest_endpoint):
    def _make_blueprints_url(image_id=None):
        base_url = "{}/customTrainingBlueprints/".format(unittest_endpoint)
        if image_id is not None:
            return "{}{}/".format(base_url, image_id)
        return base_url

    return _make_blueprints_url


def assert_blueprint(blueprint, blueprint_json):
    assert blueprint.id == blueprint_json["userBlueprintId"]

    cm_ver = blueprint_json["customModelVersion"]
    assert blueprint.custom_model_version["id"] == cm_ver["id"]
    assert blueprint.custom_model_version["label"] == cm_ver["label"]


def mock_get_response(url, response):
    responses.add(
        responses.GET, url, status=200, content_type="application/json", body=json.dumps(response),
    )


def test_from_server_data(mocked_blueprint):
    blueprint = CustomTrainingBlueprint.from_server_data(mocked_blueprint)
    assert_blueprint(blueprint, mocked_blueprint)


@responses.activate
def test_create_blueprint(mocked_blueprint, make_blueprints_url):
    responses.add(
        responses.POST,
        make_blueprints_url(),
        status=200,
        content_type="application/json",
        body=json.dumps(mocked_blueprint),
    )

    kwargs = dict(custom_model_version_id=mocked_blueprint["customModelVersion"]["id"],)
    blueprint = CustomTrainingBlueprint.create(**kwargs)
    assert_blueprint(blueprint, mocked_blueprint)

    assert responses.calls[0].request.method == "POST"
    assert responses.calls[0].request.url == make_blueprints_url()


@responses.activate
def test_create_blueprint_use_latest_version(
    mocked_blueprint, make_blueprints_url, mocked_training_model, mocked_environment
):

    responses.add(
        responses.GET,
        "https://host_name.com/customModels/{}/".format(mocked_training_model["id"]),
        body=json.dumps(mocked_training_model),
        status=200,
        content_type="application/json",
    )

    responses.add(
        responses.POST,
        make_blueprints_url(),
        status=200,
        content_type="application/json",
        body=json.dumps(mocked_blueprint),
    )

    CustomTrainingBlueprint.create(custom_model_id=mocked_blueprint["customModel"]["id"])

    assert responses.calls[0].request.method == "GET"
    assert "customModels" in responses.calls[0].request.url
    assert responses.calls[1].request.method == "POST"
    assert responses.calls[1].request.url == make_blueprints_url()
    assert (
        json.loads(responses.calls[1].request.body)["customModelVersionId"]
        == mocked_training_model["latestVersion"]["id"]
    )


@responses.activate
def test_create_clean(
    mocked_environment,
    mocked_training_model,
    mocked_custom_model_version,
    mocked_blueprint,
    make_blueprints_url,
):
    envdir = tempfile.mkdtemp()
    codedir = os.path.abspath(tempfile.mkdtemp())
    bfile = os.path.join(codedir, "bfile")
    cfile = os.path.join(codedir, "cfile")
    open(os.path.join(envdir, "afile"), "w").write("content")
    open(bfile, "w").write("content")
    open(cfile, "w").write("content")

    responses.add(
        responses.POST,
        "https://host_name.com/executionEnvironments/",
        body=json.dumps(mocked_environment),
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        "https://host_name.com/executionEnvironments/{}/".format(mocked_environment["id"]),
        body=json.dumps(mocked_environment),
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.POST,
        "https://host_name.com/executionEnvironments/{}/versions/".format(mocked_environment["id"]),
        body=json.dumps({"id": "abc123"}),
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        "https://host_name.com/executionEnvironments/{}/versions/{}/".format(
            mocked_environment["id"], "abc123"
        ),
        body=json.dumps(
            {"build_status": "success", "environment_id": mocked_environment["id"], "id": "abc123"}
        ),
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.POST,
        "https://host_name.com/customModels/",
        body=json.dumps(mocked_training_model),
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.POST,
        "https://host_name.com/customModels/{}/versions/".format(mocked_training_model["id"]),
        body=json.dumps(mocked_custom_model_version),
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.POST,
        make_blueprints_url(),
        status=200,
        content_type="application/json",
        body=json.dumps(mocked_blueprint),
    )
    blueprint = CustomTrainingBlueprint.create_from_scratch(
        name="hi",
        environment_dir=envdir,
        training_code_files=[bfile, cfile],
        target_type=TARGET_TYPE.REGRESSION,
    )
    assert_blueprint(blueprint, mocked_blueprint)


@responses.activate
def test_list_blueprints(mocked_blueprints, make_blueprints_url):
    url = make_blueprints_url()
    mock_get_response(url, mocked_blueprints)

    blueprints = CustomTrainingBlueprint.list()

    assert len(blueprints) == len(mocked_blueprints["data"])
    for image, mocked_image in zip(blueprints, mocked_blueprints["data"]):
        assert_blueprint(image, mocked_image)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url == url


@responses.activate
def test_list_blueprints_multiple_pages(mocked_blueprints, make_blueprints_url):
    url1 = make_blueprints_url()
    url2 = make_blueprints_url() + "2"

    mocked_images_2nd = deepcopy(mocked_blueprints)
    mocked_blueprints["next"] = url2

    mock_get_response(url1, mocked_blueprints)
    mock_get_response(url2, mocked_images_2nd)

    blueprints = CustomTrainingBlueprint.list()
    assert len(blueprints) == len(mocked_blueprints["data"]) + len(mocked_images_2nd["data"])
    for image, mocked_image in zip(
        blueprints, mocked_blueprints["data"] + mocked_images_2nd["data"]
    ):
        assert_blueprint(image, mocked_image)

    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.url.endswith(url1)
    assert responses.calls[1].request.method == "GET"
    assert responses.calls[1].request.url.endswith(url2)


@responses.activate
def test_from_dropin(
    mocked_environment,
    mocked_custom_model_version,
    make_blueprints_url,
    mocked_training_model,
    mocked_blueprint,
):
    envdir = tempfile.mkdtemp()
    codedir = os.path.abspath(tempfile.mkdtemp())
    bfile = os.path.join(codedir, "bfile")
    cfile = os.path.join(codedir, "cfile")
    open(os.path.join(envdir, "afile"), "w").write("content")
    open(bfile, "w").write("content")
    open(cfile, "w").write("content")

    responses.add(
        responses.POST,
        "https://host_name.com/customModels/",
        body=json.dumps(mocked_training_model),
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.POST,
        "https://host_name.com/customModels/{}/versions/".format(mocked_training_model["id"]),
        body=json.dumps(mocked_custom_model_version),
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.POST,
        make_blueprints_url(),
        status=200,
        content_type="application/json",
        body=json.dumps(mocked_blueprint),
    )
    responses.add(
        responses.GET,
        "https://host_name.com/customModels/{}/".format(mocked_training_model["id"]),
        body=json.dumps(mocked_training_model),
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        "https://host_name.com/executionEnvironments/{}/".format(mocked_environment["id"]),
        body=json.dumps(mocked_environment),
        status=200,
        content_type="application/json",
    )
    blueprint = CustomTrainingBlueprint.create_from_dropin(
        model_name="dave",
        dropin_env_id=mocked_environment["id"],
        target_type=TARGET_TYPE.REGRESSION,
        training_code_files=[bfile, cfile],
    )
    assert blueprint.id == mocked_blueprint["userBlueprintId"]
    assert blueprint.filenames == [bfile, cfile]
