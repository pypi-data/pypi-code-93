import pytest
from unittest.mock import MagicMock, patch

from azureml.automl.dnn.nlp.classification.multiclass import runner

from ...mocks import aml_dataset_mock, MockRun, multiclass_trainer_mock


@pytest.mark.usefixtures('MulticlassDatasetTester')
@pytest.mark.parametrize('multiple_text_column', [True, False])
@pytest.mark.parametrize('include_label_col', [True])
class TestMulticlassRunner:
    """Tests for Multiclass runner."""

    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoModelForSequenceClassification")
    @patch("azureml.automl.dnn.nlp.common._model_selector.AutoMLPretrainedDNNProvider")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.parse_settings")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.Run")
    def test_runner_test(
            self,
            run_mock,
            parse_settings_mock,
            get_by_id_mock,
            provider_mock,
            model_mock,
            trainer_mock,
            MulticlassDatasetTester
    ):
        # run mock
        mock_run = MockRun()
        run_mock.get_context.return_value = mock_run

        # settings mock
        automl_settings = {
            "task_type": "text-classification",
            "primary_metric": "accuracy",
            "dataset_id": "mock_dataset_id",
            "validation_dataset_id": "mock_validation_dataset_id",
            "label_column_name": "labels_col"
        }
        mock_settings = MagicMock()
        mock_settings.dataset_id = "mock_dataset_id"
        mock_settings.validation_dataset_id = "mock_validation_dataset_id"
        mock_settings.label_column_name = "labels_col"
        parse_settings_mock.return_value = mock_settings

        # dataset get_by_id mock
        input_df = MulticlassDatasetTester.get_data().copy()
        mock_file_dataset = aml_dataset_mock(input_df)
        get_by_id_mock.return_value = mock_file_dataset

        # provider mock
        provider = MagicMock()
        provider.get_model_dirname.return_value = "data/bert-base-cased"
        provider_mock.return_value = provider

        # model mock
        model = MagicMock()
        model.from_pretrained.return_value = MagicMock()
        model_mock.return_value = model

        # trainer mock
        mock_trainer = multiclass_trainer_mock()
        trainer_mock.return_value = mock_trainer

        # Test runner
        runner.run(automl_settings)

        # Asserts
        mock_trainer.train.assert_called_once()
        mock_trainer.save_model.assert_called_once()
        mock_trainer.save_state.assert_called_once()
        assert mock_trainer.log_metrics.call_count == 2
        assert mock_trainer.save_metrics.call_count == 2
