# encoding: utf-8
import json

import pytest
import responses

from datarobot._experimental import DiscardedFeaturesInfo, Project
from datarobot.errors import ClientError


@pytest.fixture
def async_url():
    return "https://host_name.com/status/status-id/"


@pytest.fixture
def discarded_features_url(unittest_endpoint, project_id):
    return "{}/projects/{}/discardedFeatures/".format(unittest_endpoint, project_id)


@pytest.fixture
def restore_discarded_features_url(unittest_endpoint, project_id):
    return "{}/projects/{}/modelingFeatures/fromDiscardedFeatures/".format(
        unittest_endpoint, project_id
    )


@pytest.fixture
def modeling_features_url(unittest_endpoint, project_id):
    return "{}/projects/{}/modelingFeatures/".format(unittest_endpoint, project_id)


@pytest.fixture
def modeling_features_server_data():
    return {
        "count": 3,
        "next": None,
        "previous": None,
        "data": [
            {
                "name": "Forecast Distance",
                "featureType": "Numeric",
                "importance": -0.0010749349695204913,
                "lowInformation": False,
                "naCount": 0,
                "dateFormat": None,
                "projectId": "60e5b3a30be17315e6c596be",
                "targetLeakage": "SKIPPED_DETECTION",
                "targetLeakageReason": "no target leakage was detected",
                "featureLineageId": None,
                "isZeroInflated": False,
                "uniqueCount": 7,
                "mean": 4.0,
                "median": 4.0,
                "min": 1.0,
                "max": 7.0,
                "stdDev": 2.0,
                "dataQualities": "NO_ISSUES_FOUND",
                "isRestoredAfterReduction": False,
                "parentFeatureNames": [],
            },
            {
                "name": "input4 (days from timestamp) (7 day mean)",
                "featureType": "Numeric",
                "importance": None,
                "lowInformation": True,
                "naCount": 0,
                "dateFormat": None,
                "projectId": "60e5b3a30be17315e6c596be",
                "targetLeakage": "SKIPPED_DETECTION",
                "targetLeakageReason": "no target leakage was detected",
                "featureLineageId": "60e5b49a777fbdf3e64060b7",
                "isZeroInflated": False,
                "uniqueCount": 1,
                "mean": 3.0,
                "median": 3.0,
                "min": 3.0,
                "max": 3.0,
                "stdDev": 0.0,
                "dataQualities": "NOT_ANALYZED",
                "isRestoredAfterReduction": True,
                "parentFeatureNames": ["target"],
            },
            {
                "name": "input4 (days from timestamp) (7 day min)",
                "featureType": "Categorical",
                "importance": 0.00023327083548663197,
                "lowInformation": False,
                "naCount": 28,
                "dateFormat": None,
                "projectId": "60e5b3a30be17315e6c596be",
                "targetLeakage": "SKIPPED_DETECTION",
                "targetLeakageReason": "no target leakage was detected",
                "featureLineageId": "60e5b49a777fbdf3e64060a6",
                "isZeroInflated": False,
                "uniqueCount": 3,
                "mean": None,
                "median": None,
                "min": None,
                "max": None,
                "stdDev": None,
                "dataQualities": "NOT_ANALYZED",
                "isRestoredAfterReduction": True,
                "parentFeatureNames": ["ідентифікатор"],
            },
        ],
    }


@pytest.fixture
def discarded_features_server_data():
    return {
        "totalRestoreLimit": 5,
        "remainingRestoreLimit": 3,
        "count": 3,
        "features": [
            "input4 (days from timestamp) (7 day mean)",
            "input4 (days from timestamp) (7 day min)",
            "input4 (days from timestamp) (7 day std)",
        ],
    }


@pytest.fixture
def discarded_features_response(discarded_features_url, discarded_features_server_data):
    responses.add(
        responses.GET,
        discarded_features_url,
        status=200,
        content_type="application/json",
        body=json.dumps(discarded_features_server_data),
    )


@pytest.fixture
def get_modeling_features_response(modeling_features_url, modeling_features_server_data):
    responses.add(
        responses.GET,
        modeling_features_url,
        status=200,
        content_type="application/json",
        body=json.dumps(modeling_features_server_data),
    )


@pytest.fixture
def restore_discarded_features_response(
    restore_discarded_features_url, async_url, modeling_features_url
):
    responses.add(
        responses.POST,
        restore_discarded_features_url,
        status=202,
        content_type="application/json",
        adding_headers={"Location": async_url},
        body="",
    )
    responses.add(
        responses.GET,
        async_url,
        body="",
        status=303,
        adding_headers={"Location": modeling_features_url},
        content_type="application/json",
    )


@pytest.fixture
def discarded_features_not_found_response(discarded_features_url):
    responses.add(
        responses.GET,
        discarded_features_url,
        status=404,
        content_type="application/json",
        body=json.dumps({"message": "no discarded features info"}),
    )


@pytest.fixture
def discarded_features_not_allowed_response(discarded_features_url):
    responses.add(
        responses.GET,
        discarded_features_url,
        status=422,
        content_type="application/json",
        body=json.dumps({"message": "Segmented project is not allowed"}),
    )


@responses.activate
@pytest.mark.usefixtures("discarded_features_response")
def test_retrieve_discarded_features(project_id):
    project = Project(project_id)
    discarded_feature_info = project.get_discarded_features()
    assert discarded_feature_info.features == [
        "input4 (days from timestamp) (7 day mean)",
        "input4 (days from timestamp) (7 day min)",
        "input4 (days from timestamp) (7 day std)",
    ]
    assert discarded_feature_info.count == len(discarded_feature_info.features)
    assert discarded_feature_info.remaining_restore_limit == 3
    assert discarded_feature_info.total_restore_limit == 5


@responses.activate
@pytest.mark.usefixtures("discarded_features_not_found_response")
def test_retrieve_no_discarded_features(project_id):
    with pytest.raises(ClientError):
        DiscardedFeaturesInfo.retrieve(project_id)


@responses.activate
@pytest.mark.usefixtures("discarded_features_not_allowed_response")
def test_retrieve_segmented_project_not_allowed(project_id):
    with pytest.raises(ClientError):
        DiscardedFeaturesInfo.retrieve(project_id)


@responses.activate
@pytest.mark.usefixtures("restore_discarded_features_response", "get_modeling_features_response")
def test_restore_discarded_features(project_id):
    project = Project(project_id)
    modeling_features = project.restore_discarded_features(
        ["input4 (days from timestamp) (7 day mean)", "input4 (days from timestamp) (7 day min)"]
    )
    assert len(modeling_features) == 3
    assert modeling_features[0].is_restored_after_reduction is False
    assert modeling_features[1].is_restored_after_reduction is True
    assert modeling_features[2].is_restored_after_reduction is True
