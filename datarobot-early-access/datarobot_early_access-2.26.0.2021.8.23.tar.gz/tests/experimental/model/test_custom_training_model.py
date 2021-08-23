import pytest
import responses

from datarobot._experimental import CustomTrainingModel
from tests.model.test_custom_model import assert_custom_model_common, mock_get_response


@pytest.fixture
def mocked_training_model(mocked_models):
    return mocked_models["data"][0]


def assert_training_model(model, model_json):
    assert_custom_model_common(model, model_json)
    assert model._model_type == "training"


class TestCustomTrainingModel(object):
    def test_from_server_data(self, mocked_training_model):
        model = CustomTrainingModel.from_server_data(mocked_training_model)
        assert_training_model(model, mocked_training_model)

    @responses.activate
    def test_get_version(self, mocked_training_model, make_models_url):
        # arrange
        url = make_models_url(mocked_training_model["id"])
        mock_get_response(url, mocked_training_model)

        # act
        model = CustomTrainingModel.get(mocked_training_model["id"])

        # assert
        assert_training_model(model, mocked_training_model)

        assert responses.calls[0].request.method == "GET"
        assert responses.calls[0].request.url == url
