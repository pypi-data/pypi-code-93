from copy import deepcopy
import json

import pytest
import responses

from datarobot.enums import CUSTOM_MODEL_TARGET_TYPE, CUSTOM_TASK_TARGET_TYPE
from datarobot.models.custom_task import CustomTask
from datarobot.utils import camelize
from tests.model.utils import assert_custom_task, assert_single_api_call, change_response_value


@pytest.fixture
def all_tasks_url(unittest_endpoint):
    return "{}/customTasks/".format(unittest_endpoint)


@pytest.fixture
def single_task_url(unittest_endpoint, custom_task_id):
    return "{}/customTasks/{}/".format(unittest_endpoint, custom_task_id)


def add_mock_get_response(url, json_dict):
    add_mock_response(responses.GET, url, json.dumps(json_dict))


def add_mock_response(method, url, body="", status=200):
    responses.add(method, url, status=status, content_type="application/json", body=body)


@pytest.fixture()
def task_get_response(single_task_url, custom_task_response_json):
    add_mock_get_response(single_task_url, custom_task_response_json)


class TestCustomTaskGetActions:
    def test_from_server_data_minimal_response(self, custom_task):
        assert custom_task["latestVersion"] is None
        assert "calibratePredictions" not in custom_task

        task = CustomTask.from_server_data(custom_task)
        assert_custom_task(task, custom_task)

    def test_from_server_data_full_response(self, custom_task_with_optional_values):
        assert custom_task_with_optional_values["latestVersion"]
        assert "calibratePredictions" in custom_task_with_optional_values

        task = CustomTask.from_server_data(custom_task_with_optional_values)
        assert_custom_task(task, custom_task_with_optional_values)

    @responses.activate
    @pytest.mark.usefixtures("task_get_response")
    def test_get_custom_task_version(self, custom_task_response_json, custom_task_id):
        task_id = custom_task_response_json["id"]
        custom_task = CustomTask.get(task_id)
        assert_custom_task(custom_task, custom_task_response_json)

        assert_single_api_call(
            responses.calls, responses.GET, "/customTasks/{}/".format(task_id),
        )

    @responses.activate
    def test_refresh_custom_task(self, custom_task_response_json, single_task_url):
        task_id = custom_task_response_json["id"]

        updated_response = {
            key: change_response_value(value) for key, value in custom_task_response_json.items()
        }
        updated_response["latestVersion"] = None

        add_mock_get_response(single_task_url, custom_task_response_json)
        add_mock_get_response(single_task_url, updated_response)

        version = CustomTask.get(task_id)

        assert len(responses.calls) == 1
        assert_custom_task(version, custom_task_response_json)

        version.refresh()

        assert len(responses.calls) == 2
        assert_custom_task(version, updated_response)

    @responses.activate
    def test_list_response_single_list(self, custom_task_list_response, all_tasks_url):
        add_mock_get_response(all_tasks_url, custom_task_list_response)
        result = CustomTask.list()
        assert len(result) == len(custom_task_list_response["data"])
        for actual, expected in zip(result, custom_task_list_response["data"]):
            assert_custom_task(actual, expected)

        assert_single_api_call(responses.calls, responses.GET, "/customTasks/")

    @responses.activate
    def test_list_response_multi_list(
        self, custom_task_list_response, custom_task_id, all_tasks_url
    ):
        next_page = deepcopy(custom_task_list_response)
        next_data = next_page["data"]
        for el in next_data:
            for key in el:
                if key != "latestVersion":
                    el[key] = change_response_value(el[key])

        next_url = "https://www.coolguy.com/coolness/"
        custom_task_list_response["next"] = next_url
        add_mock_get_response(all_tasks_url, custom_task_list_response)
        add_mock_get_response(next_url, next_page)
        result = CustomTask.list(custom_task_id)
        assert len(result) == len(custom_task_list_response["data"]) * 2
        for actual, expected in zip(result, custom_task_list_response["data"] + next_data):
            assert_custom_task(actual, expected)

    @responses.activate
    def test_list_response_search_for(self, custom_task_list_response, all_tasks_url):
        add_mock_get_response(all_tasks_url, custom_task_list_response)
        CustomTask.list(search_for="abc")

        assert_single_api_call(responses.calls, responses.GET, "/customTasks/?searchFor=abc")

    @responses.activate
    def test_list_response_order_by(self, custom_task_list_response, all_tasks_url):
        add_mock_get_response(all_tasks_url, custom_task_list_response)
        CustomTask.list(order_by="abc")

        assert_single_api_call(responses.calls, responses.GET, "/customTasks/?orderBy=abc")

    @responses.activate
    @pytest.mark.usefixtures("task_get_response")
    def test_download_latest_version(self, temporary_file, single_task_url, custom_task_id):
        target_url = single_task_url + "download/"
        content = b"some stuff"
        add_mock_response(responses.GET, target_url, content)
        version = CustomTask.get(custom_task_id)
        version.download_latest_version(temporary_file)
        with open(temporary_file, "rb") as f:
            assert f.read() == content

        calls_after_get = responses.calls[1:]
        expected_url = "customTasks/{}/download/".format(custom_task_id)
        assert_single_api_call(calls_after_get, responses.GET, expected_url)


class TestCustomTaskCopyDelete:
    @responses.activate
    def test_copy(self, all_tasks_url, custom_task_id, custom_task_response_json):
        custom_task_response_json["id"] = custom_task_id + "xyz"
        target_url = all_tasks_url + "fromCustomTask/"

        expected_ending = "customTasks/fromCustomTask/"
        expected_body = {"customTaskId": custom_task_id}

        add_mock_response(responses.POST, target_url, body=json.dumps(custom_task_response_json))
        task = CustomTask.copy(custom_task_id)
        print(task)

        assert_single_api_call(responses.calls, responses.POST, expected_ending, expected_body)
        assert_custom_task(task, custom_task_response_json)

    @responses.activate
    @pytest.mark.usefixtures("task_get_response")
    def test_delete(self, single_task_url, custom_task_id):
        add_mock_response(responses.DELETE, single_task_url, status=204)
        task = CustomTask.get(custom_task_id)
        task.delete()

        expected_ending = "customTasks/{}/".format(custom_task_id)
        assert_single_api_call(responses.calls[1:], responses.DELETE, expected_ending)


class TestCustomTaskUpdateCreate:
    @responses.activate
    @pytest.mark.usefixtures("task_get_response")
    def test_update(self, single_task_url, custom_task_id, custom_task_response_json):
        """name description language, **kwargs"""
        updated_json = deepcopy(custom_task_response_json)
        updated_json["name"] = "my crrrrrraaaaazy new name!!!!"
        updated_json["language"] = "strongly-typed-python(I can dream)"
        updated_json["description"] = "test_update description which is so awesome"

        add_mock_response(responses.PATCH, single_task_url, body=json.dumps(updated_json))

        task = CustomTask.get(custom_task_id)
        passed_name = "eric"
        passed_language = "#@$#@$!"
        passed_description = "is so cool"
        task.update(passed_name, passed_language, passed_description)

        calls_after_get = responses.calls[1:]
        expected_url_ending = "customTasks/{}/".format(task.id)
        expected_request_body = {
            "name": passed_name,
            "language": passed_language,
            "description": passed_description,
        }
        assert_single_api_call(
            calls_after_get, responses.PATCH, expected_url_ending, expected_request_body
        )

        assert_custom_task(task, updated_json)

    @responses.activate
    @pytest.mark.usefixtures("task_get_response")
    @pytest.mark.parametrize("single_kwarg", ["name", "language", "description", "hidden_stuff"])
    def test_update_single_value(
        self, single_task_url, custom_task_id, custom_task_response_json, single_kwarg
    ):
        add_mock_response(
            responses.PATCH, single_task_url, body=json.dumps(custom_task_response_json)
        )
        kwarg_value = "only the {}".format(single_kwarg)
        version = CustomTask.get(custom_task_id)
        version.update(**{single_kwarg: kwarg_value})

        call = responses.calls[1]
        assert json.loads(call.request.body) == {camelize(single_kwarg): kwarg_value}

    @responses.activate
    def test_create_task_minimum(self, all_tasks_url, custom_task_response_json):
        add_mock_response(responses.POST, all_tasks_url, body=json.dumps(custom_task_response_json))

        name = "yo!"
        target_type = CUSTOM_TASK_TARGET_TYPE.BINARY
        task = CustomTask.create(name, target_type)
        expected_body = {"name": name, "targetType": "Binary"}

        assert_single_api_call(responses.calls, responses.POST, "customTasks/", expected_body)
        assert_custom_task(task, custom_task_response_json)

    @responses.activate
    def test_create_task_all_positional_args(self, all_tasks_url, custom_task_response_json):
        add_mock_response(responses.POST, all_tasks_url, body=json.dumps(custom_task_response_json))

        name = "yo!"
        target_type = CUSTOM_TASK_TARGET_TYPE.TRANSFORM
        language = "something"
        description = "hi"
        calibrate_predictions = True

        task = CustomTask.create(name, target_type, language, description, calibrate_predictions)
        expected_body = {
            "name": name,
            "targetType": "Transform",
            "language": language,
            "description": description,
            "calibratePredictions": calibrate_predictions,
        }

        assert_single_api_call(responses.calls, responses.POST, "customTasks/", expected_body)
        assert_custom_task(task, custom_task_response_json)

    @responses.activate
    @pytest.mark.parametrize("target_type", CUSTOM_TASK_TARGET_TYPE.ALL)
    def test_create_task_all_target_types(
        self, all_tasks_url, custom_task_response_json, target_type
    ):
        assert target_type in [
            "Binary",
            "Anomaly",
            "Regression",
            "Multiclass",
            "Transform",
        ]
        add_mock_response(responses.POST, all_tasks_url, body=json.dumps(custom_task_response_json))

        name = "yo!"

        task = CustomTask.create(name, target_type)
        expected_body = {"name": name, "targetType": target_type}

        assert_single_api_call(responses.calls, responses.POST, "customTasks/", expected_body)
        assert_custom_task(task, custom_task_response_json)

    @pytest.mark.parametrize(
        "target_type",
        [CUSTOM_MODEL_TARGET_TYPE.UNSTRUCTURED] + [el + "x" for el in CUSTOM_TASK_TARGET_TYPE.ALL],
    )
    def test_create_task_illegal_target_types(self, target_type):

        name = "yabba-dabba!"
        with pytest.raises(ValueError):
            CustomTask.create(name, target_type)

    @responses.activate
    @pytest.mark.usefixtures("task_get_response")
    @pytest.mark.parametrize(
        "single_kwarg", ["calibrate_predictions", "language", "description", "hidden_stuff"]
    )
    def test_create_transform_kwargs(self, all_tasks_url, custom_task_response_json, single_kwarg):
        add_mock_response(responses.POST, all_tasks_url, body=json.dumps(custom_task_response_json))
        value = "{} is great".format(single_kwarg)
        if single_kwarg == "calibrate_predictions":
            value = False
        kwargs = {single_kwarg: value}
        name = "ajsdkfl!"
        target_type = CUSTOM_TASK_TARGET_TYPE.BINARY
        expected_body = {"name": name, "targetType": target_type, camelize(single_kwarg): value}

        CustomTask.create(name, target_type, **kwargs)

        assert_single_api_call(responses.calls, responses.POST, "customTasks/", expected_body)
