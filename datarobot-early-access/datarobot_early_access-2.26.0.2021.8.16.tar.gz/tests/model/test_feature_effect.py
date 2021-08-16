import json

import pytest
import responses

from datarobot import DatetimeModel, enums, errors, Model
from datarobot.models.feature_effect import (
    FeatureEffectMetadata,
    FeatureEffectMetadataDatetime,
    FeatureEffects,
)


@pytest.fixture
def feature_effect_metadata():
    return {"status": "COMPLETED", "sources": ["training", "validation", "holdout"]}


@pytest.fixture
def feature_effect_metadata_datetime():
    return {
        "data": [
            {"backtestIndex": "0", "status": "COMPLETED", "sources": ["training", "validation"]},
            {
                "backtestIndex": "holdout",
                "status": "NOT_COMPLETED",
                "sources": ["training", "holdout"],
            },
        ]
    }


@pytest.fixture
def feature_effect_server_data():
    return {
        "projectId": "project_id",
        "modelId": "model_id",
        "source": "training",
        "featureEffects": [
            {
                "featureType": "numeric",
                "predictedVsActual": {
                    "isCapped": False,
                    "data": [
                        {
                            "rowCount": 46.5,
                            "actual": 16,
                            "predicted": 15,
                            "label": "[ 1872, 1879 )",
                            "bin": ["1872", "1879"],
                        },
                        {
                            "rowCount": 31.5,
                            "actual": 752,
                            "predicted": 799.43,
                            "label": "[ 1879, 1886 )",
                            "bin": ["1879", "1886"],
                        },
                        {
                            "rowCount": 0.0,
                            "actual": None,
                            "predicted": None,
                            "label": "[ 1879, 1886 )",
                            "bin": ["1879", "1886"],
                        },
                    ],
                },
                "partialDependence": {
                    "isCapped": False,
                    "data": [
                        {"dependence": 41.25, "label": "1999"},
                        {"dependence": 40.64, "label": "1928"},
                        {"dependence": 41.44, "label": "nan"},
                    ],
                },
                "featureName": "record_min_temp_year",
                "weightLabel": None,
                "featureImpactScore": 1,
            },
            {
                "featureType": "categorical",
                "predictedVsActual": {
                    "isCapped": False,
                    "data": [
                        {"rowCount": 99, "actual": 4107, "predicted": 4110.0, "label": "1"},
                        {"rowCount": 98, "actual": 4175, "predicted": 4119.0, "label": "0"},
                    ],
                },
                "partialDependence": {
                    "isCapped": False,
                    "data": [
                        {"dependence": 41.13, "label": "1"},
                        {"dependence": 41.91, "label": "0"},
                        {"dependence": 41.92, "label": "=Other Unseen="},
                    ],
                },
                "featureName": "date (Day of Week)",
                "weightLabel": None,
                "featureImpactScore": 0.2,
            },
            {
                "featureType": "categorical",
                "partialDependence": {
                    "isCapped": False,
                    "data": [
                        {"dependence": 41.13, "label": "1"},
                        {"dependence": 41.91, "label": "0"},
                        {"dependence": 41.92, "label": "=Other Unseen="},
                    ],
                },
                "featureName": "date (Day of Week) no pvsa",
                "weightLabel": None,
                "featureImpactScore": 0.1,
            },
        ],
    }


@pytest.fixture
def feature_effect_server_data_holdout(feature_effect_server_data):
    feature_effect_server_data_holdout = dict(feature_effect_server_data)
    feature_effect_server_data_holdout["source"] = "holdout"
    return feature_effect_server_data_holdout


@pytest.fixture
def feature_effect_server_data_datetime(feature_effect_server_data):

    feature_effect_server_data_datetime = dict(feature_effect_server_data)
    feature_effect_server_data_datetime["backtestIndex"] = "0"
    return feature_effect_server_data_datetime


@pytest.fixture
def feature_effect_server_data_datetime_holdout(feature_effect_server_data_datetime):
    feature_effect_server_data_datetime_holdout = dict(feature_effect_server_data_datetime)
    feature_effect_server_data_datetime_holdout["source"] = "holdout"
    return feature_effect_server_data_datetime_holdout


@pytest.fixture
def feature_effect_response(feature_effect_server_data, feature_effect_url):
    source = "training"
    body = json.dumps(feature_effect_server_data)
    responses.add(
        responses.GET,
        "{}?source={}".format(feature_effect_url, source),
        status=200,
        content_type="application/json",
        body=body,
    )


@pytest.fixture
def feature_effect_response_holdout(feature_effect_server_data_holdout, feature_effect_url):
    source = "holdout"
    body = json.dumps(feature_effect_server_data_holdout)
    responses.add(
        responses.GET,
        "{}?source={}".format(feature_effect_url, source),
        status=200,
        content_type="application/json",
        body=body,
    )


@pytest.fixture
def feature_effect_invalid_request_response(feature_effect_url):
    source = "invalid"
    body = {"message": "Invalid source"}

    responses.add(
        responses.GET,
        "{}?source={}".format(feature_effect_url, source),
        status=404,
        content_type="application/json",
        body=json.dumps(body),
    )


@pytest.fixture
def feature_effect_response_datetime(
    feature_effect_server_data_datetime, feature_effect_url_datetime
):
    source = "training"
    backtest_index = "0"
    responses.add(
        responses.GET,
        "{}?source={}&backtestIndex=".format(feature_effect_url_datetime, source, backtest_index),
        status=200,
        content_type="application/json",
        body=json.dumps(feature_effect_server_data_datetime),
    )


@pytest.fixture
def feature_effect_response_holdout_datetime(
    feature_effect_server_data_datetime_holdout, feature_effect_url_datetime
):
    source = "training"
    backtest_index = "0"
    responses.add(
        responses.GET,
        "{}?source={}&backtestIndex=".format(feature_effect_url_datetime, source, backtest_index),
        status=200,
        content_type="application/json",
        body=json.dumps(feature_effect_server_data_datetime_holdout),
    )


@pytest.fixture
def feature_effect_invalid_request_response_datetime(feature_effect_url_datetime):
    body = {"message": "Invalid source"}

    source = "invalid"
    backtest_index = "0"
    responses.add(
        responses.GET,
        "{}?source={}&backtestIndex=".format(feature_effect_url_datetime, source, backtest_index),
        status=404,
        content_type="application/json",
        body=json.dumps(body),
    )


@pytest.fixture
def feature_effect_metadata_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/featureEffectsMetadata/".format(
        project_id, model_id
    )


@pytest.fixture
def feature_effect_metadata_url_datetime(project_id, model_id):
    return "https://host_name.com/projects/{}/datetimeModels/{}/featureEffectsMetadata/".format(
        project_id, model_id
    )


@pytest.fixture
def feature_effect_url(project_id, model_id):
    return "https://host_name.com/projects/{}/models/{}/featureEffects/".format(
        project_id, model_id
    )


@pytest.fixture
def feature_effect_url_datetime(project_id, model_id):
    return "https://host_name.com/projects/{}/datetimeModels/{}/featureEffects/".format(
        project_id, model_id
    )


@pytest.fixture
def feature_effect_job_running_server_data(base_job_running_server_data):
    return dict(base_job_running_server_data, jobType=enums.JOB_TYPE.FEATURE_EFFECTS)


@pytest.fixture
def feature_effect_job_finished_server_data(base_job_completed_server_data):
    return dict(base_job_completed_server_data, jobType=enums.JOB_TYPE.FEATURE_EFFECTS)


@pytest.fixture
def feature_effect_job_creation_response(feature_effect_url, job_url):
    responses.add(
        responses.POST,
        feature_effect_url,
        body="",
        status=202,
        adding_headers={"Location": job_url},
    )


@pytest.fixture
def feature_effect_job_creation_bad_request(feature_effect_url):
    body = {"message": "Invalid field data", "errors": {"rowCount": "value is less than 10"}}
    responses.add(
        responses.POST,
        feature_effect_url,
        status=422,
        content_type="application/json",
        body=json.dumps(body),
    )


@pytest.fixture
def feature_effect_job_creation_response_datetime(feature_effect_url_datetime, job_url):
    responses.add(
        responses.POST,
        feature_effect_url_datetime,
        body=json.dumps({"backtestIndex": "0"}),
        status=202,
        adding_headers={"Location": job_url},
        content_type="application/json",
    )


@pytest.fixture
def feature_effect_completed_response(
    feature_effect_job_finished_server_data, job_url, feature_effect_url
):
    """
    Loads a response that the given job is a featureImpact job, and is in completed
    """
    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(feature_effect_job_finished_server_data),
        status=303,
        adding_headers={"Location": feature_effect_url},
        content_type="application/json",
    )


@pytest.fixture
def feature_effect_completed_response_datetime(
    feature_effect_job_finished_server_data, job_url, feature_effect_url_datetime
):
    """
    Loads a response that the given job is a featureImpact job, and is in completed
    """
    feature_effect_url_datetime_with_backtest = "{}?backtestIndex={}".format(
        feature_effect_url_datetime, "0"
    )
    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(feature_effect_job_finished_server_data),
        status=303,
        adding_headers={"Location": feature_effect_url_datetime_with_backtest},
        content_type="application/json",
    )


@pytest.fixture
def feature_effect_running_response(feature_effect_job_running_server_data, job_url):
    """
    Loads a response that the given job is a featureEffects job, and is running
    """
    responses.add(
        responses.GET,
        job_url,
        body=json.dumps(feature_effect_job_running_server_data),
        status=200,
        content_type="application/json",
    )


@pytest.fixture
def feature_effect_previously_ran_response(feature_effect_url, job_id):
    """
    Loads a response that the given model has already ran its feature effect
     """
    body = {
        "message": "Feature Effect is in progress for this model.",
        "errorName": "JobAlreadyAdded",
        "jobId": job_id,
    }
    responses.add(
        responses.POST,
        feature_effect_url,
        body=json.dumps(body),
        status=422,
        content_type="application/json",
    )


@pytest.fixture
def feature_effect_previously_ran_response_datetime(feature_effect_url_datetime, job_id):
    """
    Loads a response that the given model has already ran its feature effect
     """
    body = {
        "message": "Feature Effect is in progress for this model.",
        "errorName": "JobAlreadyAdded",
        "jobId": job_id,
    }
    responses.add(
        responses.POST,
        feature_effect_url_datetime,
        body=json.dumps(body),
        status=422,
        content_type="application/json",
    )


def test_get_feature_effect_metadata_url(project_id, model_id):
    model = Model(id=model_id, project_id=project_id)
    expected_fe_meatadata_url = "projects/{}/models/{}/featureEffectsMetadata/".format(
        project_id, model_id
    )
    assert model._get_feature_effect_metadata_url() == expected_fe_meatadata_url


def test_get_feature_effect_metadata_url_datetime(project_id, model_id):
    model = DatetimeModel(id=model_id, project_id=project_id)
    expected_fe_meatadata_url = "projects/{}/datetimeModels/{}/featureEffectsMetadata/".format(
        project_id, model_id
    )
    assert model._get_feature_effect_metadata_url() == expected_fe_meatadata_url


@responses.activate
def test_get_feature_effect_metadata(
    feature_effect_metadata, feature_effect_metadata_url, project_id, model_id
):
    responses.add(
        responses.GET,
        feature_effect_metadata_url,
        status=200,
        content_type="application/json",
        body=json.dumps(feature_effect_metadata),
    )
    model = Model(id=model_id, project_id=project_id)
    fe_metadata = model.get_feature_effect_metadata()

    assert isinstance(fe_metadata, FeatureEffectMetadata)
    assert fe_metadata.status == feature_effect_metadata["status"]
    assert fe_metadata.sources == feature_effect_metadata["sources"]


@responses.activate
def test_get_feature_effect_metadata_datetime(
    feature_effect_metadata_datetime, feature_effect_metadata_url_datetime, project_id, model_id,
):
    responses.add(
        responses.GET,
        feature_effect_metadata_url_datetime,
        status=200,
        content_type="application/json",
        body=json.dumps(feature_effect_metadata_datetime),
    )
    model = DatetimeModel(id=model_id, project_id=project_id)
    fe_metadata = model.get_feature_effect_metadata()

    assert isinstance(fe_metadata, FeatureEffectMetadataDatetime)
    assert len(fe_metadata.data) == len(feature_effect_metadata_datetime["data"])
    feature_effect_metadata_datetime_sorted = sorted(
        feature_effect_metadata_datetime["data"], key=lambda k: k["backtestIndex"]
    )
    for i, meta in enumerate(sorted(fe_metadata)):
        assert meta.backtest_index == feature_effect_metadata_datetime_sorted[i]["backtestIndex"]
        assert meta.status == feature_effect_metadata_datetime_sorted[i]["status"]
        assert sorted(meta.sources) == sorted(feature_effect_metadata_datetime_sorted[i]["sources"])


@responses.activate
@pytest.mark.usefixtures("feature_effect_job_creation_response", "feature_effect_running_response")
def test_get_feature_effect_job_result_not_finished(one_model):
    feature_effect_job = one_model.request_feature_effect()
    with pytest.raises(errors.JobNotFinished):
        feature_effect_job.get_result()


@responses.activate
@pytest.mark.usefixtures("feature_effect_job_creation_bad_request")
def test_request_feature_effect_bad_payload(one_model):
    with pytest.raises(errors.ClientError):
        one_model.request_feature_effect(row_count=0)


@responses.activate
@pytest.mark.usefixtures(
    "feature_effect_job_creation_response",
    "feature_effect_completed_response",
    "feature_effect_response",
)
def test_get_feature_effect_job_result_finished(feature_effect_server_data, one_model):
    feature_effect_job = one_model.request_feature_effect(row_count=3200)
    feature_effect = feature_effect_job.get_result()
    assert feature_effect.project_id == feature_effect_server_data["projectId"]
    assert feature_effect.model_id == feature_effect_server_data["modelId"]
    assert feature_effect.source == feature_effect_server_data["source"]
    assert feature_effect.project_id == feature_effect_server_data["projectId"]
    assert len(feature_effect.feature_effects) == len(feature_effect_server_data["featureEffects"])

    expected_fe = FeatureEffects.from_server_data(feature_effect_server_data)
    assert expected_fe == feature_effect


@responses.activate
@pytest.mark.usefixtures(
    "feature_effect_response_holdout",
    "feature_effect_job_creation_response",
    "feature_effect_completed_response",
)
def test_get_feature_effect_job_result_finished_holdout(
    feature_effect_server_data_holdout, one_model
):
    feature_effect_job = one_model.request_feature_effect()
    params = {"source": "holdout"}
    feature_effect = feature_effect_job.get_result(params)
    assert feature_effect.project_id == feature_effect_server_data_holdout["projectId"]
    assert feature_effect.model_id == feature_effect_server_data_holdout["modelId"]
    assert feature_effect.source == feature_effect_server_data_holdout["source"]
    assert feature_effect.project_id == feature_effect_server_data_holdout["projectId"]
    assert len(feature_effect.feature_effects) == len(
        feature_effect_server_data_holdout["featureEffects"]
    )

    expected_fe = FeatureEffects.from_server_data(feature_effect_server_data_holdout)
    assert expected_fe == feature_effect


@responses.activate
@pytest.mark.usefixtures("feature_effect_job_creation_response", "feature_effect_running_response")
def test_wait_for_feature_effect_never_finished(one_model, mock_async_time):
    mock_async_time.time.side_effect = (0, 5)
    feature_effect_job = one_model.request_feature_effect()
    with pytest.raises(errors.AsyncTimeoutError):
        feature_effect_job.get_result_when_complete(max_wait=1)


@responses.activate
@pytest.mark.usefixtures(
    "feature_effect_previously_ran_response",
    "feature_effect_completed_response",
    "feature_effect_response",
)
def test_get_or_request_feature_effect_previously_requested(one_model, feature_effect_server_data):
    feature_effect = one_model.get_or_request_feature_effect(source="training")
    assert feature_effect.project_id == feature_effect_server_data["projectId"]
    assert feature_effect.model_id == feature_effect_server_data["modelId"]
    assert feature_effect.source == feature_effect_server_data["source"]
    assert feature_effect.project_id == feature_effect_server_data["projectId"]
    assert len(feature_effect.feature_effects) == len(feature_effect_server_data["featureEffects"])

    expected_fe = FeatureEffects.from_server_data(feature_effect_server_data)
    assert expected_fe == feature_effect


@responses.activate
@pytest.mark.usefixtures(
    "feature_effect_previously_ran_response", "feature_effect_running_response"
)
def test_get_or_request_feature_effect_currently_running_waits(one_model, mock_async_time):
    mock_async_time.time.side_effect = (0, 5)
    with pytest.raises(errors.AsyncTimeoutError):
        one_model.get_or_request_feature_effect(max_wait=1, source="training")


@responses.activate
@pytest.mark.usefixtures(
    "feature_effect_job_creation_response",
    "feature_effect_completed_response",
    "feature_effect_response",
)
def test_get_or_request_feature_effect(one_model, feature_effect_server_data):

    feature_effect = one_model.get_or_request_feature_effect(source="training", row_count=3200)
    assert feature_effect.project_id == feature_effect_server_data["projectId"]
    assert feature_effect.model_id == feature_effect_server_data["modelId"]
    assert feature_effect.source == feature_effect_server_data["source"]
    assert feature_effect.project_id == feature_effect_server_data["projectId"]
    assert len(feature_effect.feature_effects) == len(feature_effect_server_data["featureEffects"])

    expected_fe = FeatureEffects.from_server_data(feature_effect_server_data)
    assert expected_fe == feature_effect


@responses.activate
@pytest.mark.usefixtures("feature_effect_job_creation_bad_request")
def test_get_or_request_feature_effect_bad_payload(one_model):
    with pytest.raises(errors.ClientError):
        one_model.get_or_request_feature_effect(source="training", row_count=1000000)


@responses.activate
@pytest.mark.usefixtures(
    "client",
    "feature_effect_job_creation_response",
    "feature_effect_completed_response",
    "feature_effect_response",
)
def test_wait_for_feature_effect_finished(one_model, feature_effect_server_data):
    params = {"source": "training"}
    feature_effect_job = one_model.request_feature_effect()
    feature_effect = feature_effect_job.get_result_when_complete(max_wait=0.5, params=params)

    assert feature_effect.project_id == feature_effect_server_data["projectId"]
    assert feature_effect.model_id == feature_effect_server_data["modelId"]
    assert feature_effect.source == feature_effect_server_data["source"]
    assert feature_effect.project_id == feature_effect_server_data["projectId"]
    assert len(feature_effect.feature_effects) == len(feature_effect_server_data["featureEffects"])

    expected_fe = FeatureEffects.from_server_data(feature_effect_server_data)
    assert expected_fe == feature_effect


@responses.activate
@pytest.mark.usefixtures("feature_effect_response")
def test_get_feature_effect_assumed_complete(one_model, feature_effect_server_data):
    feature_effect = one_model.get_feature_effect(source="training")

    assert feature_effect.project_id == feature_effect_server_data["projectId"]
    assert feature_effect.model_id == feature_effect_server_data["modelId"]
    assert feature_effect.source == feature_effect_server_data["source"]
    assert feature_effect.project_id == feature_effect_server_data["projectId"]
    assert len(feature_effect.feature_effects) == len(feature_effect_server_data["featureEffects"])

    expected_fe = FeatureEffects.from_server_data(feature_effect_server_data)
    assert expected_fe == feature_effect


@responses.activate
@pytest.mark.usefixtures("feature_effect_invalid_request_response")
def test_get_feature_effect_invalid_source(one_model):
    with pytest.raises(errors.ClientError):
        one_model.get_feature_effect(source="invalid")


@responses.activate
@pytest.mark.usefixtures(
    "feature_effect_job_creation_response_datetime", "feature_effect_running_response"
)
def test_get_feature_effect_job_result_not_finished_datetime(one_datetime_model):
    backtest_index = "0"
    feature_effect_job = one_datetime_model.request_feature_effect(backtest_index)
    with pytest.raises(errors.JobNotFinished):
        feature_effect_job.get_result()


@responses.activate
@pytest.mark.usefixtures(
    "feature_effect_job_creation_response_datetime",
    "feature_effect_completed_response_datetime",
    "feature_effect_response_datetime",
)
def test_get_feature_effect_job_result_finished_datetime(
    feature_effect_server_data_datetime, one_datetime_model
):
    backtest_index = "0"
    source = "training"
    params = {"source": source}
    feature_effect_job = one_datetime_model.request_feature_effect(backtest_index)
    feature_effect = feature_effect_job.get_result(params)
    assert feature_effect.project_id == feature_effect_server_data_datetime["projectId"]
    assert feature_effect.model_id == feature_effect_server_data_datetime["modelId"]
    assert feature_effect.source == feature_effect_server_data_datetime["source"]
    assert feature_effect.project_id == feature_effect_server_data_datetime["projectId"]
    assert feature_effect.backtest_index == feature_effect_server_data_datetime["backtestIndex"]
    assert len(feature_effect.feature_effects) == len(
        feature_effect_server_data_datetime["featureEffects"]
    )

    expected_fe = FeatureEffects.from_server_data(feature_effect_server_data_datetime)
    assert expected_fe == feature_effect


@responses.activate
@pytest.mark.usefixtures(
    "feature_effect_response_holdout_datetime",
    "feature_effect_job_creation_response_datetime",
    "feature_effect_completed_response_datetime",
)
def test_get_feature_effect_job_result_finished_holdout_datetime(
    feature_effect_server_data_datetime_holdout, one_datetime_model
):
    backtest_index = "0"
    feature_effect_job = one_datetime_model.request_feature_effect(backtest_index)
    params = {"source": "holdout"}
    feature_effect = feature_effect_job.get_result(params)
    assert feature_effect.project_id == feature_effect_server_data_datetime_holdout["projectId"]
    assert feature_effect.model_id == feature_effect_server_data_datetime_holdout["modelId"]
    assert feature_effect.source == feature_effect_server_data_datetime_holdout["source"]
    assert feature_effect.project_id == feature_effect_server_data_datetime_holdout["projectId"]
    assert (
        feature_effect.backtest_index
        == feature_effect_server_data_datetime_holdout["backtestIndex"]
    )
    assert len(feature_effect.feature_effects) == len(
        feature_effect_server_data_datetime_holdout["featureEffects"]
    )

    expected_fe = FeatureEffects.from_server_data(feature_effect_server_data_datetime_holdout)
    assert expected_fe == feature_effect


@responses.activate
@pytest.mark.usefixtures(
    "feature_effect_job_creation_response_datetime", "feature_effect_running_response"
)
def test_wait_for_feature_effect_never_finished_datetime(one_datetime_model, mock_async_time):
    backtest_index = "0"
    mock_async_time.time.side_effect = (0, 5)
    feature_effect_job = one_datetime_model.request_feature_effect(backtest_index)
    with pytest.raises(errors.AsyncTimeoutError):
        feature_effect_job.get_result_when_complete(max_wait=1)


@responses.activate
@pytest.mark.usefixtures(
    "feature_effect_previously_ran_response_datetime",
    "feature_effect_completed_response_datetime",
    "feature_effect_response_datetime",
)
def test_get_or_request_feature_effect_previously_requested_datetime(
    one_datetime_model, feature_effect_server_data_datetime
):
    backtest_index = "0"
    source = "training"
    feature_effect = one_datetime_model.get_or_request_feature_effect(
        source=source, backtest_index=backtest_index
    )
    assert feature_effect.project_id == feature_effect_server_data_datetime["projectId"]
    assert feature_effect.model_id == feature_effect_server_data_datetime["modelId"]
    assert feature_effect.source == feature_effect_server_data_datetime["source"]
    assert feature_effect.project_id == feature_effect_server_data_datetime["projectId"]
    assert len(feature_effect.feature_effects) == len(
        feature_effect_server_data_datetime["featureEffects"]
    )
    assert feature_effect.backtest_index == feature_effect_server_data_datetime["backtestIndex"]
    expected_fe = FeatureEffects.from_server_data(feature_effect_server_data_datetime)
    assert expected_fe == feature_effect


@responses.activate
@pytest.mark.usefixtures(
    "feature_effect_previously_ran_response_datetime", "feature_effect_running_response"
)
def test_get_or_request_feature_effect_currently_running_waits_datetime(
    one_datetime_model, mock_async_time
):
    backtest_index = "0"
    source = "training"
    mock_async_time.time.side_effect = (0, 5)
    with pytest.raises(errors.AsyncTimeoutError):
        one_datetime_model.get_or_request_feature_effect(
            source=source, backtest_index=backtest_index, max_wait=1
        )


@responses.activate
@pytest.mark.usefixtures(
    "feature_effect_job_creation_response_datetime",
    "feature_effect_completed_response_datetime",
    "feature_effect_response_datetime",
)
def test_get_or_request_feature_effect_datetime(
    one_datetime_model, feature_effect_server_data_datetime
):
    backtest_index = "0"
    source = "training"
    feature_effect = one_datetime_model.get_or_request_feature_effect(
        source=source, backtest_index=backtest_index
    )
    assert feature_effect.project_id == feature_effect_server_data_datetime["projectId"]
    assert feature_effect.model_id == feature_effect_server_data_datetime["modelId"]
    assert feature_effect.source == feature_effect_server_data_datetime["source"]
    assert feature_effect.project_id == feature_effect_server_data_datetime["projectId"]
    assert len(feature_effect.feature_effects) == len(
        feature_effect_server_data_datetime["featureEffects"]
    )
    assert feature_effect.backtest_index == feature_effect_server_data_datetime["backtestIndex"]
    expected_fe = FeatureEffects.from_server_data(feature_effect_server_data_datetime)
    assert expected_fe == feature_effect


@responses.activate
@pytest.mark.usefixtures(
    "client",
    "feature_effect_job_creation_response_datetime",
    "feature_effect_completed_response_datetime",
    "feature_effect_response_datetime",
)
def test_wait_for_feature_effect_finished_datetime(
    one_datetime_model, feature_effect_server_data_datetime
):
    params = {"source": "training"}
    backtest_index = "0"
    feature_effect_job = one_datetime_model.request_feature_effect(backtest_index)
    feature_effect = feature_effect_job.get_result_when_complete(max_wait=0.5, params=params)
    assert feature_effect.project_id == feature_effect_server_data_datetime["projectId"]
    assert feature_effect.model_id == feature_effect_server_data_datetime["modelId"]
    assert feature_effect.source == feature_effect_server_data_datetime["source"]
    assert feature_effect.project_id == feature_effect_server_data_datetime["projectId"]
    assert feature_effect.backtest_index == feature_effect_server_data_datetime["backtestIndex"]
    assert len(feature_effect.feature_effects) == len(
        feature_effect_server_data_datetime["featureEffects"]
    )
    expected_fe = FeatureEffects.from_server_data(feature_effect_server_data_datetime)
    assert expected_fe == feature_effect


@responses.activate
@pytest.mark.usefixtures("feature_effect_response_datetime")
def test_get_feature_effect_assumed_complete_datetime(
    one_datetime_model, feature_effect_server_data_datetime
):
    backtest_index = "0"
    source = "invalid"
    feature_effect = one_datetime_model.get_feature_effect(
        source=source, backtest_index=backtest_index
    )
    assert feature_effect.project_id == feature_effect_server_data_datetime["projectId"]
    assert feature_effect.model_id == feature_effect_server_data_datetime["modelId"]
    assert feature_effect.source == feature_effect_server_data_datetime["source"]
    assert feature_effect.project_id == feature_effect_server_data_datetime["projectId"]
    assert feature_effect.backtest_index == feature_effect_server_data_datetime["backtestIndex"]
    assert len(feature_effect.feature_effects) == len(
        feature_effect_server_data_datetime["featureEffects"]
    )
    expected_fe = FeatureEffects.from_server_data(feature_effect_server_data_datetime)
    assert expected_fe == feature_effect


@responses.activate
@pytest.mark.usefixtures("feature_effect_invalid_request_response_datetime")
def test_get_feature_effect_invalid_source_datetime(one_datetime_model):
    backtest_index = "0"
    source = "invalid"
    with pytest.raises(errors.ClientError):
        one_datetime_model.get_feature_effect(source=source, backtest_index=backtest_index)
