import pytest
import unittest
from unittest.mock import MagicMock, patch, mock_open

import numpy as np

from azureml.automl.dnn.nlp.common.constants import NERModelParameters
from azureml.automl.dnn.nlp.ner.inference.score import score
from azureml.data import FileDataset
from ..mocks import aml_dataset_mock, get_labeling_df, MockLabelingRun, MockRun


@pytest.mark.usefixtures('new_clean_dir')
class NERScoreTests(unittest.TestCase):
    """Tests for NER scorer."""

    @patch("azureml.automl.dnn.nlp.ner.inference.score.open")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.DatasetWrapper")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.Trainer")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.get_labels")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoModelForTokenClassification")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoConfig")
    @patch("azureml.automl.dnn.nlp.common.utils.Run")
    def test_score(
            self, run_mock, config_mock, tokenizer_mock, model_mock, get_by_id_mock,
            get_labels_mock, trainer_mock, dataset_mock, open_mock
    ):
        mock_run = MockRun()
        run_mock.get_context.return_value = mock_run
        run_mock.download_file.return_value = None
        config_mock.from_pretrained.return_value = MagicMock()
        tokenizer_mock.from_pretrained.return_value = MagicMock()
        model_mock.from_pretrained.return_value = MagicMock()
        dataset_mock = MagicMock(FileDataset)
        dataset_mock.download.return_value = MagicMock()
        dataset_mock.to_path.return_value = ["/sample_test.txt"]
        get_by_id_mock.return_value = dataset_mock

        label_list = ["O", "B-MISC", "I-MISC", "B-PER"]
        get_labels_mock.return_value = label_list

        trainer = MagicMock()
        batch_size = 3
        seq_len = NERModelParameters.MAX_SEQ_LENGTH
        predictions = np.random.rand(batch_size, seq_len, len(label_list))
        label_ids = np.random.randint(0, high=len(label_list), size=(batch_size, seq_len))
        trainer.predict.return_value = predictions, label_ids, {"metrics": 0.5}
        trainer.is_world_process_zero.return_value = True
        trainer_mock.return_value = trainer
        open_mock.return_value = MagicMock()

        score(
            mock_run.id,
            "mock_dataset_id",
            "ner_data",
            "output_dir"
        )
        self.assertEqual(open_mock.call_count, 3)

    @patch("azureml.automl.dnn.nlp.ner.inference.score.open")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.DatasetWrapper")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.Trainer")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.get_labels")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoModelForTokenClassification")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoConfig")
    @patch("azureml.automl.dnn.nlp.common.utils.Run")
    def test_score_no_metric(
            self, run_mock, config_mock, tokenizer_mock, model_mock, get_by_id_mock,
            get_labels_mock, trainer_mock, dataset_mock, open_mock
    ):
        mock_run = MockRun()
        run_mock.get_context.return_value = mock_run
        run_mock.download_file.return_value = None
        config_mock.from_pretrained.return_value = MagicMock()
        tokenizer_mock.from_pretrained.return_value = MagicMock()
        model_mock.from_pretrained.return_value = MagicMock()
        dataset_mock = MagicMock(FileDataset)
        dataset_mock.download.return_value = MagicMock()
        dataset_mock.to_path.return_value = ["/sample_test.txt"]
        get_by_id_mock.return_value = dataset_mock

        label_list = ["O", "B-MISC", "I-MISC", "B-PER"]
        get_labels_mock.return_value = label_list

        trainer = MagicMock()
        batch_size = 3
        seq_len = NERModelParameters.MAX_SEQ_LENGTH
        predictions = np.random.rand(batch_size, seq_len, len(label_list))
        label_ids = np.random.randint(0, high=len(label_list), size=(batch_size, seq_len))
        trainer.predict.return_value = predictions, label_ids, None
        trainer.is_world_process_zero.return_value = True
        trainer_mock.return_value = trainer

        score(
            mock_run.id,
            "mock_dataset_id",
            "ner_data",
            "output_dir"
        )
        self.assertEqual(open_mock.call_count, 2)

    @patch("azureml.automl.dnn.nlp.ner.inference.score.generate_results_for_labeling_service")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.load_test_dataset_for_labeling_service")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.DatasetWrapper")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.Trainer")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.get_labels")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoModelForTokenClassification")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoConfig")
    @patch("azureml.automl.dnn.nlp.common.utils.Run")
    def test_score_labeling_service(
            self, run_mock, config_mock, tokenizer_mock, model_mock, get_by_id_mock,
            get_labels_mock, trainer_mock, dataset_mock, load_test_dataset_for_labeling_service_mock,
            generate_results_for_labeling_service_mock
    ):
        mock_run = MockLabelingRun()
        run_mock.return_value = mock_run

        config_mock.from_pretrained.return_value = MagicMock()
        tokenizer_mock.from_pretrained.return_value = MagicMock()
        model_mock.from_pretrained.return_value = MagicMock()

        mock_dataset = aml_dataset_mock(get_labeling_df())
        get_by_id_mock.return_value = mock_dataset

        label_list = ["B-LOC", "B-PER", "I-LOC", "I-PER", "O"]
        get_labels_mock.return_value = label_list

        trainer = MagicMock()
        batch_size = 2
        seq_len = NERModelParameters.MAX_SEQ_LENGTH
        # Create fake predictions
        predictions = np.random.rand(batch_size, seq_len, len(label_list))
        label_ids = np.random.randint(0, high=len(label_list), size=(batch_size, seq_len))
        trainer.predict.return_value = predictions, label_ids, {"metrics": 0.5}
        trainer.is_world_process_zero.return_value = True
        trainer_mock.return_value = trainer

        load_test_dataset_for_labeling_service_mock.return_value = "test.txt", ["sample1.txt", "sample2.txt"]

        open_mock = mock_open()
        with patch("builtins.open", open_mock):
            score(
                mock_run.id,
                "mock_dataset_id",
                "ner_data",
                "output_dir"
            )
        self.assertTrue(load_test_dataset_for_labeling_service_mock.call_count == 1)
        self.assertEquals(
            generate_results_for_labeling_service_mock.call_args[0],
            ("output_dir", "predictions.txt", ["sample1.txt", "sample2.txt"])
        )


if __name__ == "__main__":
    unittest.main()
