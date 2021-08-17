import pytest
import unittest
from unittest.mock import MagicMock, patch

from azureml.automl.dnn.nlp.ner import runner


from ..mocks import aml_dataset_mock, file_dataset_mock, get_labeling_df, MockLabelingRun, MockRun, ner_trainer_mock


@pytest.mark.usefixtures('new_clean_dir')
class NERRunnerTests(unittest.TestCase):
    """Tests for NER trainer."""

    @patch("azureml.automl.dnn.nlp.ner.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoModelForTokenClassification")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoMLPretrainedDNNProvider")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.ner.runner.parse_settings")
    @patch("azureml.automl.dnn.nlp.ner.runner.Run")
    def test_runner(
            self,
            run_mock,
            parse_settings_mock,
            get_by_id_mock,
            provider_mock,
            model_mock,
            trainer_mock
    ):
        # run mock
        mock_run = MockRun()
        run_mock.get_context.return_value = mock_run

        # settings mock
        automl_settings = {
            "task_type": "text-ner",
            "primary_metric": "accuracy",
            "dataset_id": "mock_dataset_id",
            "validation_dataset_id": "mock_validation_dataset_id"
        }
        mock_settings = MagicMock()
        mock_settings.dataset_id = "mock_dataset_id"
        mock_settings.validation_dataset_id = "mock_validation_dataset_id"
        parse_settings_mock.return_value = mock_settings

        # dataset get_by_id mock
        mock_file_dataset = file_dataset_mock()
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
        mock_trainer = ner_trainer_mock()
        trainer_mock.return_value = mock_trainer

        # Test runner
        runner.run(automl_settings)

        # Asserts
        mock_trainer.train.assert_called_once()
        mock_trainer.save_model.assert_called_once()
        self.assertEqual(mock_trainer.log_metrics.call_count, 2)
        self.assertEqual(mock_trainer.save_metrics.call_count, 2)
        mock_trainer.save_state.assert_called_once()

    @patch("azureml.automl.dnn.nlp.ner.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoModelForTokenClassification")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoMLPretrainedDNNProvider")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.ner.runner.parse_settings")
    @patch("azureml.automl.dnn.nlp.ner.runner.Run.get_context")
    def test_runner_labeling_service(
            self,
            run_mock,
            parse_settings_mock,
            get_by_id_mock,
            provider_mock,
            model_mock,
            trainer_mock
    ):
        # run mock
        mock_run = MockLabelingRun()
        run_mock.return_value = mock_run

        # settings mock
        automl_settings = {
            "task_type": "text-ner",
            "primary_metric": "accuracy",
            "dataset_id": "mock_dataset_id",
            "validation_dataset_id": "mock_validation_dataset_id"
        }
        mock_settings = MagicMock()
        mock_settings.dataset_id = "mock_dataset_id"
        mock_settings.validation_dataset_id = "mock_validation_dataset_id"
        parse_settings_mock.return_value = mock_settings

        # dataset get_by_id mock
        mock_dataset = aml_dataset_mock(get_labeling_df())
        get_by_id_mock.return_value = mock_dataset

        # provider mock
        provider = MagicMock()
        provider.get_model_dirname.return_value = "data/bert-base-cased"
        provider_mock.return_value = provider

        # model mock
        model = MagicMock()
        model.from_pretrained.return_value = MagicMock()
        model_mock.return_value = model

        # trainer mock
        mock_trainer = ner_trainer_mock()
        trainer_mock.return_value = mock_trainer

        # Test runner
        runner.run(automl_settings)

        # Asserts
        mock_trainer.train.assert_called_once()
        mock_trainer.save_model.assert_called_once()
        self.assertEqual(mock_trainer.log_metrics.call_count, 2)
        self.assertEqual(mock_trainer.save_metrics.call_count, 2)
        mock_trainer.save_state.assert_called_once()


if __name__ == "__main__":
    unittest.main()
