import pandas as pd
import pytest
import unittest
from unittest.mock import MagicMock, patch
from azureml.automl.dnn.nlp.classification.common.constants import DatasetLiterals
from azureml.automl.dnn.nlp.classification.io.read.dataloader import (
    _concat_text_and_preserve_label,
    dataset_loader,
    multiclass_dataset_loader
)
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import PyTorchMulticlassDatasetWrapper
from ...mocks import aml_dataset_mock
try:
    import torch
    has_torch = True
except ImportError:
    has_torch = False


@pytest.mark.usefixtures('MulticlassDatasetTester')
class TestTextClassificationDataLoadTests:
    """Tests for Text Classification data loader."""
    @pytest.mark.parametrize('multiple_text_column', [False])
    @pytest.mark.parametrize('include_label_col', [True, False])
    def test_concat_text_and_preserve_label(self, MulticlassDatasetTester, include_label_col):
        input_df = MulticlassDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        if include_label_col:
            # One text column, along with label column (training scenario)
            assert input_df.shape == (5, 2)
            output_df = _concat_text_and_preserve_label(input_df, label_column_name)
            assert output_df.shape == (5, 2)
            assert set(output_df.columns) == set([label_column_name, DatasetLiterals.TEXT_COLUMN])
        else:
            # One text column, no label column (inference scenario)
            assert input_df.shape == (5, 1)
            output_df = _concat_text_and_preserve_label(input_df, label_column_name)
            assert output_df.shape == (5, 1)
            assert set(output_df.columns) == set([DatasetLiterals.TEXT_COLUMN])

    @pytest.mark.parametrize('multiple_text_column', [True])
    @pytest.mark.parametrize('include_label_col', [True, False])
    def test_concat_text_and_preserve_label_multiple_text_cols(self, MulticlassDatasetTester, include_label_col):
        input_df = MulticlassDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        if include_label_col:
            # Two text columns, along with label column (training scenario)
            assert input_df.shape == (5, 3)
            output_df = _concat_text_and_preserve_label(input_df, label_column_name)
            assert output_df.shape == (5, 2)
            assert set(output_df.columns) == set([label_column_name, DatasetLiterals.TEXT_COLUMN])
        else:
            # Two text columns, no label column (inference scenario)
            assert input_df.shape == (5, 2)
            output_df = _concat_text_and_preserve_label(input_df, label_column_name)
            assert output_df.shape == (5, 1)
            assert set(output_df.columns) == set([DatasetLiterals.TEXT_COLUMN])

    @unittest.skipIf(not has_torch, "torch not installed")
    @pytest.mark.parametrize('multiple_text_column', [False])
    @pytest.mark.parametrize('include_label_col', [True])
    @patch("azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper.preprocess_function")
    @patch("azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper.get_model_from_language")
    def test_pytorch_multiclass_dataset_wrapper(self, language_mock, preprocess_mock,
                                                tokenizer_mock, MulticlassDatasetTester):
        input_df = MulticlassDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        assert input_df.shape == (5, 2)
        output_dataframe = _concat_text_and_preserve_label(input_df, label_column_name)
        assert type(output_dataframe) == pd.DataFrame
        label_list = pd.unique(output_dataframe[label_column_name])
        preprocessing_result = {'input_ids': [[101], [1188], [1110], [170], [1353]],
                                'token_type_ids': [[0], [0], [0], [0], [0]],
                                'attention_mask': [[1], [1], [1], [1], [1]],
                                'labels': [[0], [0], [0], [0], [0]]}
        preprocess_mock.return_value = preprocessing_result
        tokenizer_mock.from_pretrained.return_value.model_max_length = 256
        language_mock.return_value = ('some_model_name', 'some_path_name')
        output_set = PyTorchMulticlassDatasetWrapper(output_dataframe, label_list,
                                                     'eng', label_column_name)
        assert type(output_set) == PyTorchMulticlassDatasetWrapper
        assert set(output_dataframe.columns) == set([label_column_name, DatasetLiterals.TEXT_COLUMN])
        assert len(output_set) == 5
        assert tokenizer_mock.from_pretrained.call_args[0][0] == "some_model_name"
        assert all(output_set_curr.keys() == set([DatasetLiterals.LABEL_COLUMN,
                                                  DatasetLiterals.INPUT_IDS,
                                                  DatasetLiterals.TOKEN_TYPE_IDS,
                                                  DatasetLiterals.ATTENTION_MASK]) for output_set_curr in output_set)
        for output_set_curr in output_set:
            for key_name in output_set_curr.keys():
                assert type(output_set_curr[key_name]) == torch.Tensor

    @pytest.mark.parametrize('multiple_text_column', [True, False])
    @pytest.mark.parametrize('include_label_col', [True])
    @patch("azureml.core.Dataset.get_by_id")
    def test_dataset_loader(self, get_by_id_mock, MulticlassDatasetTester):
        input_df = MulticlassDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        mock_aml_dataset = aml_dataset_mock(input_df)
        get_by_id_mock.return_value = mock_aml_dataset
        dataset_id = "mock_id"
        validation_dataset_id = "mock_validation_id"
        aml_workspace_mock = MagicMock()
        training_set, validation_set, label_list = dataset_loader(dataset_id, validation_dataset_id,
                                                                  label_column_name, aml_workspace_mock,
                                                                  dataset_language='eng',
                                                                  is_multiclass_training=True)
        # The returned label_list is sorted, although the original labels weren't
        assert label_list != input_df[label_column_name].unique().tolist()
        assert label_list == sorted(input_df[label_column_name].unique())
        for output_set in [training_set, validation_set]:
            assert type(output_set) == PyTorchMulticlassDatasetWrapper
            assert len(output_set) == 5
            assert all(output_set_curr.keys() ==
                       set([DatasetLiterals.LABEL_COLUMN, DatasetLiterals.INPUT_IDS, DatasetLiterals.TOKEN_TYPE_IDS,
                            DatasetLiterals.ATTENTION_MASK]) for output_set_curr in output_set)

    @pytest.mark.parametrize('multiple_text_column', [True, False])
    @pytest.mark.parametrize('include_label_col', [True])
    def test_multiclass_dataset_loader(self, MulticlassDatasetTester, MulticlassValDatasetTester):
        train_df = MulticlassDatasetTester.get_data().copy()
        label_column_name = "labels_col"

        # Test Case 1: when validation data contains label classes not in the train data
        val_df = MulticlassValDatasetTester.get_data().copy()
        training_set, validation_set, label_list = multiclass_dataset_loader(train_df, val_df,
                                                                             'eng', label_column_name)
        assert label_list == ['ABC', 'DEF', 'PQR', 'XYZ']
        for output_set in [training_set, validation_set]:
            assert type(output_set) == PyTorchMulticlassDatasetWrapper
            assert len(output_set) == 5
            assert all(output_set_curr.keys() ==
                       set([DatasetLiterals.LABEL_COLUMN, DatasetLiterals.INPUT_IDS, DatasetLiterals.TOKEN_TYPE_IDS,
                            DatasetLiterals.ATTENTION_MASK]) for output_set_curr in output_set)

        # Test Case 2: when validation data contains label classes identical to the train data
        val_df = MulticlassDatasetTester.get_data().copy()
        training_set, validation_set, label_list = multiclass_dataset_loader(train_df, val_df,
                                                                             'eng', label_column_name)
        assert label_list == ['ABC', 'PQR', 'XYZ']
        for output_set in [training_set, validation_set]:
            assert type(output_set) == PyTorchMulticlassDatasetWrapper
            assert len(output_set) == 5
            assert all(output_set_curr.keys() ==
                       set([DatasetLiterals.LABEL_COLUMN, DatasetLiterals.INPUT_IDS, DatasetLiterals.TOKEN_TYPE_IDS,
                            DatasetLiterals.ATTENTION_MASK]) for output_set_curr in output_set)

        # Test Case 3: when validation data is missing
        val_df = None
        training_set, validation_set, label_list = multiclass_dataset_loader(train_df, val_df,
                                                                             'eng', label_column_name)
        assert label_list == ['ABC', 'PQR', 'XYZ']
        assert validation_set is None
        for output_set in [training_set]:
            assert type(output_set) == PyTorchMulticlassDatasetWrapper
            assert len(output_set) == 5
            assert all(output_set_curr.keys() ==
                       set([DatasetLiterals.LABEL_COLUMN, DatasetLiterals.INPUT_IDS, DatasetLiterals.TOKEN_TYPE_IDS,
                            DatasetLiterals.ATTENTION_MASK]) for output_set_curr in output_set)
