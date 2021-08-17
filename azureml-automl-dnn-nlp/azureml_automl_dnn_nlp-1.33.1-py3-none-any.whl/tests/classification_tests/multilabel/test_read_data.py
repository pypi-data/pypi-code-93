import pytest
import numpy as np
import unittest
from unittest.mock import MagicMock, patch

from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import PyTorchDatasetWrapper
from azureml.automl.dnn.nlp.classification.io.read.dataloader import (
    get_vectorizer,
    dataset_loader,
    multilabel_dataset_loader
)
from ...mocks import aml_dataset_mock
try:
    import torch
    has_torch = True
except ImportError:
    has_torch = False


@pytest.mark.usefixtures('MultilabelDatasetTester')
@pytest.mark.parametrize('multiple_text_column', [False])
class TestPyTorchDatasetWrapper:
    @unittest.skipIf(not has_torch, "torch not installed")
    def test_pytorch_dataset_wrapper(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        vectorizer = get_vectorizer(input_df, input_df, label_column_name)
        num_label_cols = len(vectorizer.get_feature_names())
        assert num_label_cols == 6
        training_set = PyTorchDatasetWrapper(input_df, label_column_name=label_column_name, vectorizer=vectorizer)
        assert len(training_set) == 5
        assert set(training_set[1].keys()) == set(['ids', 'mask', 'token_type_ids', 'targets'])
        assert all(torch.is_tensor(value) for key, value in training_set[1].items())

        expected_targes = vectorizer.transform([input_df["labels_col"][1]]).toarray().astype(float)[0]
        assert np.array_equal(training_set[1]['targets'].detach().numpy(), expected_targes)

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_pytorch_dataset_wrapper_for_inference(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        input_df = input_df.drop(columns=["labels_col"]).reset_index(drop=True)
        training_set = PyTorchDatasetWrapper(input_df)
        assert len(training_set) == 5
        assert set(training_set[1].keys()) == set(['ids', 'mask', 'token_type_ids'])
        assert all(torch.is_tensor(value) for key, value in training_set[1].items())

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_column_concatenation(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        vectorizer = get_vectorizer(input_df, input_df, label_column_name)
        num_label_cols = len(vectorizer.get_feature_names())
        assert num_label_cols == 6
        training_set = PyTorchDatasetWrapper(input_df, label_column_name=label_column_name, vectorizer=vectorizer)
        assert training_set._concat_text_columns(0) == "This is a small sample dataset containing cleaned text data."

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_column_concatenation_inference(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        input_df = input_df.drop(columns=["labels_col"]).reset_index(drop=True)
        training_set = PyTorchDatasetWrapper(input_df)
        assert training_set._concat_text_columns(0) == "This is a small sample dataset containing cleaned text data."

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_get_vectorizer(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        # Test both cases, with and without validation data
        for valid_df in [input_df, None]:
            vectorizer = get_vectorizer(input_df, valid_df, label_column_name)
            num_label_cols = len(vectorizer.get_feature_names())
            assert num_label_cols == 6
            assert set(vectorizer.get_feature_names()) == set(['A', 'a', '1', '2', 'label5', 'label6'])

    @unittest.skipIf(not has_torch, "torch not installed")
    @patch("azureml.core.Dataset.get_by_id")
    def test_dataset_loader(self, get_by_id_mock, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        mock_aml_dataset = aml_dataset_mock(input_df)
        get_by_id_mock.return_value = mock_aml_dataset
        dataset_id = "mock_id"
        validation_dataset_id = "mock_validation_id"
        aml_workspace_mock = MagicMock()
        training_set, validation_set, num_label_cols, _ = dataset_loader(dataset_id, validation_dataset_id,
                                                                         label_column_name, aml_workspace_mock)
        assert num_label_cols == 6
        for output_set in [training_set, validation_set]:
            assert type(output_set) == PyTorchDatasetWrapper
            assert len(output_set) == 5
            assert all(set(output_set[i].keys()) ==
                       set(['ids', 'mask', 'token_type_ids', 'targets']) for i in range(len(output_set)))

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_multilabel_dataset_loader(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        training_set, validation_set, num_label_cols, vectorizer = multilabel_dataset_loader(input_df, input_df,
                                                                                             label_column_name)
        assert num_label_cols == 6
        for output_set in [training_set, validation_set]:
            assert type(output_set) == PyTorchDatasetWrapper
            assert len(output_set) == 5
            assert all(set(output_set[i].keys()) ==
                       set(['ids', 'mask', 'token_type_ids', 'targets']) for i in range(len(output_set)))


@pytest.mark.usefixtures('MultilabelDatasetTester')
@pytest.mark.parametrize('multiple_text_column', [True])
class TestPyTorchDatasetWrapperMultipleColumnst:
    @unittest.skipIf(not has_torch, "torch not installed")
    def test_pytorch_dataset_wrapper(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        vectorizer = get_vectorizer(input_df, input_df, label_column_name)
        num_label_cols = len(vectorizer.get_feature_names())
        assert num_label_cols == 6
        training_set = PyTorchDatasetWrapper(input_df, label_column_name=label_column_name, vectorizer=vectorizer)
        assert len(training_set) == 5
        assert all(item in ['ids', 'mask', 'token_type_ids', 'targets'] for item in training_set[1])
        assert all(torch.is_tensor(value) for key, value in training_set[1].items())

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_column_concatenation(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        vectorizer = get_vectorizer(input_df, input_df, label_column_name)
        num_label_cols = len(vectorizer.get_feature_names())
        assert num_label_cols == 6
        training_set = PyTorchDatasetWrapper(input_df, label_column_name=label_column_name, vectorizer=vectorizer)
        expected = 'This is a small sample dataset containing cleaned text data. This is an additional column.'
        assert training_set._concat_text_columns(0) == expected

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_get_vectorizer(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        # Test both cases, with and without validation data
        for valid_df in [input_df, None]:
            vectorizer = get_vectorizer(input_df, valid_df, label_column_name)
            num_label_cols = len(vectorizer.get_feature_names())
            assert num_label_cols == 6
            assert set(vectorizer.get_feature_names()) == set(['A', 'a', '1', '2', 'label5', 'label6'])
