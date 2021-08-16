from datetime import datetime
import json

from dateutil.tz import tzutc
import pytest
import responses
from trafaret import DataError

from datarobot._experimental.models.segmentation import SegmentationTask

_project_id = "projectId"
_target = "target"
_model_package_id = "modelPackageId"
_current_time = "2020-01-01T01:00:01.123456Z"
_base_url = "https://host_name.com"
_create_url = "{}/projects/{}/segmentationTasks/"
_results_url = "{}/projects/{}/segmentationTasks/results/{}/"
_get_url = "{}/projects/{}/segmentationTasks/{}/"

_valid_segmentation_task_id = "segmentationTaskId"
_invalid_segmentation_task_id = "badSegmentationTaskId"
_valid_segementation_task_url = _get_url.format(_base_url, _project_id, _valid_segmentation_task_id)
_invalid_segementation_task_url = _get_url.format(
    _base_url, _project_id, _invalid_segmentation_task_id
)


@pytest.fixture
def segmentation_record():
    return {
        "projectId": _project_id,
        "segmentationTaskId": _valid_segmentation_task_id,
        "name": "testSegmentor",
        "type": "testType",
        "created": _current_time,
        "segmentsCount": 1,
        "segments": ["user_segment_1"],
        "metadata": {
            "useMultiseriesIdColumns": True,
            "useUserDefinedSegmentColumns": True,
            "useTimeSeries": True,
            "useAutomatedSegmentation": False,
        },
        "data": {
            "multiseriesIdColumns": ["series_id"],
            "userDefinedSegmentIdColumns": ["segment"],
            "datetimePartitionColumn": "date",
        },
    }


@pytest.fixture
def segmentation_failed_record():
    return {
        "name": "badTestSegmentor",
        "parameters": {"parameter": "value"},
        "message": "errorMessage",
    }


@pytest.fixture
def segmentation_results_response(segmentation_record, segmentation_failed_record):
    return {
        "numberOfJobs": 2,
        "completedJobs": [
            {
                "name": segmentation_record["name"],
                "segmentationTaskId": segmentation_record["segmentationTaskId"],
                "segmentsCount": segmentation_record["segmentsCount"],
                "url": _get_url.format(
                    _base_url,
                    segmentation_record["projectId"],
                    segmentation_record["segmentationTaskId"],
                ),
            }
        ],
        "failedJobs": [segmentation_failed_record],
    }


@pytest.fixture
def segmentation_results_response_json(segmentation_results_response):
    return json.dumps(segmentation_results_response)


@pytest.fixture
def segmentation_list_response(segmentation_record):
    return {"count": 1, "next": None, "previous": None, "data": [segmentation_record]}


@pytest.fixture
def segmentation_task_get_json(segmentation_record):
    return json.dumps(segmentation_record)


@pytest.fixture
def invalid_json():
    return json.dumps({"message": "Not Found"})


@pytest.fixture
def segmentation_task_list_json(segmentation_list_response):
    return json.dumps(segmentation_list_response)


@pytest.fixture
def automated_segmentation_record():
    return {
        "projectId": _project_id,
        "segmentationTaskId": _valid_segmentation_task_id,
        "name": "testAutomatedSegmentor",
        "type": "testType",
        "created": _current_time,
        "segmentsCount": 3,
        "segments": ["segment_1", "segment_2", "segment_3"],
        "metadata": {
            "useMultiseriesIdColumns": True,
            "useUserDefinedSegmentColumns": False,
            "useTimeSeries": True,
            "useAutomatedSegmentation": True,
        },
        "data": {
            "multiseriesIdColumns": ["series_id"],
            "datetimePartitionColumn": "date",
            "modelPackageId": _model_package_id,
        },
    }


@pytest.fixture
def automated_segmentation_task_get_json(automated_segmentation_record):
    return json.dumps(automated_segmentation_record)


@pytest.fixture
def automated_segmentation_results_response(
    automated_segmentation_record, segmentation_failed_record
):
    return {
        "numberOfJobs": 1,
        "completedJobs": [
            {
                "name": automated_segmentation_record["name"],
                "segmentationTaskId": automated_segmentation_record["segmentationTaskId"],
                "segmentsCount": automated_segmentation_record["segmentsCount"],
                "url": _get_url.format(
                    _base_url,
                    automated_segmentation_record["projectId"],
                    automated_segmentation_record["segmentationTaskId"],
                ),
            }
        ],
        "failedJobs": [segmentation_failed_record],
    }


@pytest.fixture
def automated_segmentation_results_response_json(automated_segmentation_results_response):
    return json.dumps(automated_segmentation_results_response)


def test_time_series_must_have_date(
    automated_segmentation_results_response_json, automated_segmentation_task_get_json
):
    with pytest.raises(
        ValueError, match="A datetime_partition_column value must be specified for time series."
    ):
        SegmentationTask.create(
            _project_id, _target, use_time_series=True,
        )


def test_time_series_must_have_multiseries_id(
    automated_segmentation_results_response_json, automated_segmentation_task_get_json
):
    with pytest.raises(
        ValueError, match="A multiseries_id_columns value must be specified for time series."
    ):
        SegmentationTask.create(
            _project_id, _target, use_time_series=True, datetime_partition_column="date",
        )


def test_time_series_multiseries_id_must_be_list_or_tuple(
    automated_segmentation_results_response_json, automated_segmentation_task_get_json
):
    with pytest.raises(
        ValueError, match="Expected list of str for multiseries_id_columns, got: True"
    ):
        SegmentationTask.create(
            _project_id,
            _target,
            use_time_series=True,
            datetime_partition_column="date",
            multiseries_id_columns=True,
        )


def test_segmentation_must_be_user_defined_or_automatic(
    automated_segmentation_results_response_json, automated_segmentation_task_get_json
):
    with pytest.raises(
        ValueError,
        match="Either a user_defined_segment_id_columns value or a model_package_id must "
        "be defined to create a new segmentation task.",
    ):
        SegmentationTask.create(
            _project_id,
            _target,
            use_time_series=True,
            datetime_partition_column="date",
            multiseries_id_columns=["series_id"],
        )


@responses.activate
def test_use_automated_segmentation_task_creation(
    automated_segmentation_results_response_json, automated_segmentation_task_get_json
):
    responses.add(
        responses.POST,
        _create_url.format(_base_url, _project_id),
        body="",
        status=202,
        adding_headers={"Location": "{}/status/some-status-id/".format(_base_url)},
        content_type="application_json",
    )
    responses.add(
        responses.GET,
        "{}/status/some-status-id/".format(_base_url),
        body="",
        status=303,
        adding_headers={"Location": _results_url.format(_base_url, _project_id, "resultsId")},
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        _results_url.format(_base_url, _project_id, "resultsId"),
        body=automated_segmentation_results_response_json,
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        _valid_segementation_task_url,
        body=automated_segmentation_task_get_json,
        status=200,
        content_type="application/json",
    )
    segmentation_task_results = SegmentationTask.create(
        _project_id,
        _target,
        use_time_series=True,
        datetime_partition_column="date",
        multiseries_id_columns=["series_id"],
        model_package_id=_model_package_id,
    )
    assert segmentation_task_results["numberOfJobs"] == 1
    assert len(segmentation_task_results["completedJobs"]) == 1
    segmentation_task = segmentation_task_results["completedJobs"][0]
    assert isinstance(segmentation_task, SegmentationTask)
    assert segmentation_task.id == _valid_segmentation_task_id
    assert segmentation_task.project_id == _project_id
    assert segmentation_task.created == datetime(2020, 1, 1, 1, 0, 1, 123456, tzinfo=tzutc())
    assert segmentation_task.name == "testAutomatedSegmentor"
    assert segmentation_task.type == "testType"
    assert segmentation_task.segments_count == 3
    assert segmentation_task.segments == ["segment_1", "segment_2", "segment_3"]
    assert segmentation_task.metadata == {
        "use_multiseries_id_columns": True,
        "use_user_defined_segment_columns": False,
        "use_time_series": True,
        "use_automated_segmentation": True,
    }
    assert segmentation_task.data == {
        "multiseries_id_columns": ["series_id"],
        "datetime_partition_column": "date",
        "model_package_id": "modelPackageId",
    }


@responses.activate
def test_segmentation_create(
    segmentation_results_response_json, segmentation_task_get_json, segmentation_failed_record
):
    responses.add(
        responses.POST,
        _create_url.format(_base_url, _project_id),
        body="",
        status=202,
        adding_headers={"Location": "{}/status/some-status-id/".format(_base_url)},
        content_type="application_json",
    )
    responses.add(
        responses.GET,
        "{}/status/some-status-id/".format(_base_url),
        body="",
        status=303,
        adding_headers={"Location": _results_url.format(_base_url, _project_id, "resultsId")},
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        _results_url.format(_base_url, _project_id, "resultsId"),
        body=segmentation_results_response_json,
        status=200,
        content_type="application/json",
    )
    responses.add(
        responses.GET,
        _valid_segementation_task_url,
        body=segmentation_task_get_json,
        status=200,
        content_type="application/json",
    )
    segmentation_task_results = SegmentationTask.create(
        _project_id,
        _target,
        use_time_series=True,
        datetime_partition_column="date",
        multiseries_id_columns=["series_id"],
        user_defined_segment_id_columns=["segment_id"],
    )
    assert segmentation_task_results["numberOfJobs"] == 2
    assert len(segmentation_task_results["completedJobs"]) == 1
    segmentation_task = segmentation_task_results["completedJobs"][0]

    assert isinstance(segmentation_task, SegmentationTask)
    assert segmentation_task.id == _valid_segmentation_task_id
    assert segmentation_task.project_id == _project_id
    assert segmentation_task.created == datetime(2020, 1, 1, 1, 0, 1, 123456, tzinfo=tzutc())
    assert segmentation_task.name == "testSegmentor"
    assert segmentation_task.type == "testType"
    assert segmentation_task.segments_count == 1
    assert segmentation_task.segments == ["user_segment_1"]
    assert segmentation_task.metadata == {
        "use_multiseries_id_columns": True,
        "use_user_defined_segment_columns": True,
        "use_time_series": True,
        "use_automated_segmentation": False,
    }
    assert segmentation_task.data == {
        "multiseries_id_columns": ["series_id"],
        "user_defined_segment_id_columns": ["segment"],
        "datetime_partition_column": "date",
    }

    assert segmentation_task_results["failedJobs"] == [segmentation_failed_record]


@responses.activate
def test_segmentation_list(segmentation_task_list_json):
    responses.add(
        responses.GET,
        _create_url.format(_base_url, _project_id),
        body=segmentation_task_list_json,
        status=200,
        content_type="application/json",
    )
    segmentation_tasks = SegmentationTask.list(_project_id)
    assert len(segmentation_tasks) == 1
    segmentation_task = segmentation_tasks[0]

    assert isinstance(segmentation_task, SegmentationTask)
    assert segmentation_task.id == _valid_segmentation_task_id
    assert segmentation_task.project_id == _project_id
    assert segmentation_task.created == datetime(2020, 1, 1, 1, 0, 1, 123456, tzinfo=tzutc())
    assert segmentation_task.name == "testSegmentor"
    assert segmentation_task.type == "testType"
    assert segmentation_task.segments_count == 1
    assert segmentation_task.segments == ["user_segment_1"]
    assert segmentation_task.metadata == {
        "use_multiseries_id_columns": True,
        "use_user_defined_segment_columns": True,
        "use_time_series": True,
        "use_automated_segmentation": False,
    }
    assert segmentation_task.data == {
        "multiseries_id_columns": ["series_id"],
        "user_defined_segment_id_columns": ["segment"],
        "datetime_partition_column": "date",
    }


@responses.activate
def test_segmentation_get_valid(segmentation_task_get_json):
    responses.add(
        responses.GET,
        _valid_segementation_task_url,
        body=segmentation_task_get_json,
        status=200,
        content_type="application/json",
    )
    segmentation_task = SegmentationTask.get(_project_id, _valid_segmentation_task_id)

    assert isinstance(segmentation_task, SegmentationTask)
    assert segmentation_task.id == _valid_segmentation_task_id
    assert segmentation_task.project_id == _project_id
    assert segmentation_task.created == datetime(2020, 1, 1, 1, 0, 1, 123456, tzinfo=tzutc())
    assert segmentation_task.name == "testSegmentor"
    assert segmentation_task.type == "testType"
    assert segmentation_task.segments_count == 1
    assert segmentation_task.segments == ["user_segment_1"]
    assert segmentation_task.metadata == {
        "use_multiseries_id_columns": True,
        "use_user_defined_segment_columns": True,
        "use_time_series": True,
        "use_automated_segmentation": False,
    }
    assert segmentation_task.data == {
        "multiseries_id_columns": ["series_id"],
        "user_defined_segment_id_columns": ["segment"],
        "datetime_partition_column": "date",
    }


@responses.activate
def test_segmentation_task_invalid_get(invalid_json):
    responses.add(responses.GET, _invalid_segementation_task_url, body=invalid_json)
    with pytest.raises(DataError):
        SegmentationTask.get(_project_id, _invalid_segmentation_task_id)
