import numpy as np
import pandas as pd
import pytest
from typing import NamedTuple
from unittest.mock import MagicMock, patch

from azureml.automl.dnn.nlp.classification.common.constants import DatasetLiterals
from azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer import MulticlassInferencer
from azureml.automl.dnn.nlp.classification.io.read.dataloader import _concat_text_and_preserve_label
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import PyTorchMulticlassDatasetWrapper

try:
    import torch
    has_torch = True
except ImportError:
    has_torch = False


class MockExperiment:
    def __init__(self):
        self.workspace = "some_workspace"


class MockRun:
    @property
    def experiment(self):
        return self

    @property
    def workspace(self):
        return self

    @property
    def id(self):
        return "mock_run_id"

    def RaiseError(self):
        raise ValueError()


class OutputName(NamedTuple):
    predictions: np.array


class MockTrainer:
    def __init__(self, nrows=5, ncols=3):
        self.nrows = nrows
        self.ncols = ncols

    def predict(self, test_dataset=None):
        return OutputName(predictions=np.random.rand(self.nrows, self.ncols))

    def is_world_process_zero(self):
        return True


class TestTextClassificationInferenceTests:
    """Tests for Text Classification inference."""
    @patch("azureml.automl.dnn.nlp.classification.io.write.multiclass.score_script.Run")
    @patch("azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer.PyTorchMulticlassDatasetWrapper")
    @patch("azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer.AmlDataset")
    @patch("azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer.np.load")
    @patch("azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer.AutoConfig")
    @patch("azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer.AutoModelForSequenceClassification")
    @patch("azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer.Trainer")
    @patch("azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer.MulticlassInferencer.download_file")
    @patch("azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer.get_model_from_language")
    @pytest.mark.usefixtures('MulticlassDatasetTester')
    @pytest.mark.parametrize('multiple_text_column', [True, False])
    @pytest.mark.parametrize('include_label_col', [True, False])
    def test_inference(self, langauge_mock, file_download, trainer_mock, auto_model_mock, auto_token_mock,
                       auto_config_mock, np_load_mock, aml_dataset_mock, pytorch_data_wrapper_mock, run_mock,
                       MulticlassDatasetTester, multiple_text_column, include_label_col):
        test_df = MulticlassDatasetTester.get_data().copy()
        mock_run = MockRun()
        run_mock.get_context.return_value = mock_run
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        inferencer = MulticlassInferencer(run_mock, device)

        mock_aml_dataset = MagicMock()
        mock_aml_dataset.get_by_id.return_value = MagicMock()
        aml_dataset_mock.get_by_id.return_value = mock_aml_dataset

        auto_model = MagicMock()
        auto_model.from_pretrained.return_value = MagicMock()
        auto_model_mock.return_value = auto_model

        pytorch_data_wrapper = MagicMock()
        pytorch_data_wrapper_mock.return_value = pytorch_data_wrapper

        auto_config = MagicMock()
        auto_config.from_pretrained.return_value = MagicMock()
        auto_config_mock.return_value = auto_config

        auto_token_mock.from_pretrained.return_value = MagicMock()
        file_download.return_value = MagicMock()
        langauge_mock.return_value = ('some_model_name', "some_model_path")

        np_load_mock.return_value = MagicMock()

        trainer_mock.return_value = MockTrainer()

        label_column_name = "labels_col"
        predicted_df = inferencer.score(input_dataset_id="some_dataset_id",
                                        label_column_name=label_column_name,
                                        dataset_language='some_language')
        assert aml_dataset_mock.get_by_id.call_count == 1
        assert file_download.call_count == 4
        assert auto_model_mock.from_pretrained.call_count == 1
        assert auto_config_mock.from_pretrained.call_count == 1
        assert auto_config_mock.from_pretrained.call_args[0][0] == 'some_model_name'
        assert auto_token_mock.from_pretrained.call_args[0][0] == 'some_model_name'

        inference_df = _concat_text_and_preserve_label(test_df, label_column_name)
        if include_label_col:
            label_list = pd.unique(inference_df[label_column_name])
        else:
            label_list = ['ABC', 'PQR', 'XYZ']
        mock_trainer_obj = MockTrainer(nrows=len(test_df), ncols=len(label_list))

        if label_column_name in inference_df.columns:
            inference_df.drop(columns=label_column_name, inplace=True)
        inference_data = PyTorchMulticlassDatasetWrapper(inference_df, label_list, 'eng', infer_data=True)

        predicted_df = inferencer.predict(mock_trainer_obj, inference_data, test_df, label_list, label_column_name)
        if multiple_text_column:
            assert all(column in ['text_first', 'text_second', label_column_name,
                                  DatasetLiterals.LABEL_CONFIDENCE] for column in predicted_df.columns)
            assert predicted_df.shape == (5, 4)
        else:
            assert all(column in ['text_first', label_column_name,
                                  DatasetLiterals.LABEL_CONFIDENCE] for column in predicted_df.columns)
            assert predicted_df.shape == (5, 3)
        assert all(item in label_list for item in predicted_df[label_column_name])
        assert all(item >= 0 and item <= 1 for item in predicted_df[DatasetLiterals.LABEL_CONFIDENCE])
