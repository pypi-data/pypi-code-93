import pytest
import unittest

from azureml.automl.dnn.nlp.classification.inference.multilabel_inferencer import MultilabelInferencer
from azureml.automl.dnn.nlp.classification.io.read.dataloader import get_vectorizer
from ...mocks import MockRun, MockBertClass

try:
    import torch
    has_torch = True
except ImportError:
    has_torch = False


@pytest.mark.usefixtures('MultilabelDatasetTester')
@pytest.mark.parametrize('multiple_text_column', [False, True])
class TestMultilabelInferencer:
    @unittest.skipIf(not has_torch, "torch not installed")
    def test_obtain_dataloader(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        vectorizer = get_vectorizer(input_df, input_df, label_column_name)
        num_label_cols = len(vectorizer.get_feature_names())
        assert num_label_cols == 6
        run = MockRun()
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        inferencer = MultilabelInferencer(run, device)
        inference_data_loader = inferencer.obtain_dataloader(input_df, vectorizer, label_column_name)
        assert len(inference_data_loader.dataset) == len(input_df)

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_predict(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        vectorizer = get_vectorizer(input_df, input_df, label_column_name)
        num_label_cols = len(vectorizer.get_feature_names())
        assert num_label_cols == 6
        run = MockRun()
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        inferencer = MultilabelInferencer(run, device)
        inference_data_loader = inferencer.obtain_dataloader(input_df, vectorizer, label_column_name)
        assert len(inference_data_loader.dataset) == len(input_df)
        model = MockBertClass(num_label_cols)
        predicted_df = inferencer.predict(model, vectorizer, input_df, inference_data_loader, label_column_name)
        assert len(predicted_df) == len(input_df)
