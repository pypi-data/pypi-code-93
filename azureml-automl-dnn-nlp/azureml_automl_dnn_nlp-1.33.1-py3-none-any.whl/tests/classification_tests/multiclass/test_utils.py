from datasets import Dataset
import numpy as np
import pytest
from transformers import AutoTokenizer, EvalPrediction

from unittest.mock import MagicMock, patch
from azureml.automl.dnn.nlp.classification.common.constants import (
    ModelNames,
    MultiClassParameters
)
from azureml.automl.dnn.nlp.classification.io.read.dataloader import _concat_text_and_preserve_label
from azureml.automl.dnn.nlp.classification.io.write.multiclass.score_script import _get_language
from azureml.automl.dnn.nlp.classification.multiclass.utils import compute_metrics, preprocess_function
from azureml.automl.dnn.nlp.classification.multiclass.runner import run


class TestTextClassificationTrainerTests:
    """Tests for utility functions for multi-class text classification."""
    @pytest.mark.usefixtures('MulticlassDatasetTester')
    @pytest.mark.parametrize('multiple_text_column', [True, False])
    @pytest.mark.parametrize('include_label_col', [True, False])
    def test_preprocess_function(self, MulticlassDatasetTester, include_label_col):
        input_df = MulticlassDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        input_set = Dataset.from_pandas(_concat_text_and_preserve_label(input_df, label_column_name))
        if include_label_col:
            label_list = input_set.unique(label_column_name)
        else:
            label_list = None
        fn_kwargs = {'tokenizer': AutoTokenizer.from_pretrained(ModelNames.BERT_BASE_CASED, use_fast=True),
                     'padding': MultiClassParameters.MAX_LEN_PADDING,
                     'max_seq_length': MultiClassParameters.MAX_SEQ_LENGTH,
                     'label_to_id': {v: i for i, v in enumerate(label_list)} if label_list else label_list,
                     'label_column_name': label_column_name}
        preproc_data = input_set.map(preprocess_function, batched=True, fn_kwargs=fn_kwargs)
        assert all(len(example['attention_mask']) == MultiClassParameters.MAX_SEQ_LENGTH and
                   len(example['input_ids']) == MultiClassParameters.MAX_SEQ_LENGTH and
                   len(example['token_type_ids']) == MultiClassParameters.MAX_SEQ_LENGTH for example in preproc_data)

    @pytest.mark.usefixtures('MulticlassDatasetTester')
    @pytest.mark.parametrize('multiple_text_column', [True, False])
    @pytest.mark.parametrize('include_label_col', [True, False])
    def test_compute_metrics(self, MulticlassDatasetTester, include_label_col):
        input_df = MulticlassDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        input_set = Dataset.from_pandas(_concat_text_and_preserve_label(input_df, label_column_name))
        if include_label_col:
            label_list = input_set.unique(label_column_name)
        else:
            label_list = ['ABC', 'PQR', 'XYZ']
        num_examples = len(input_df)
        predictions = np.random.rand(num_examples, len(label_list))
        label_ids = np.random.randint(0, high=len(label_list), size=num_examples)
        metrics = compute_metrics(EvalPrediction(predictions, label_ids))
        assert metrics['accuracy'] >= 0.0

    @patch("azureml.automl.dnn.nlp.classification.io.write.multiclass.score_script.Run")
    @pytest.mark.parametrize(
        'input,expected', [
            ('{"featurization":"auto"}', 'eng'),
            ('{"featurization":{"_dataset_language":"eng"}}', 'eng'),
            ('{"featurization":{"_dataset_language":"deu"}}', 'deu'),
            ('{"featurization":{"_dataset_language":"ita"}}', 'ita')]
    )
    def test_score_script_language(self, run_mock, input, expected):
        run_mock.parent.parent.properties = {"AMLSettingsJsonString": input}
        language = _get_language(run_mock)
        assert language == expected

    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.parse_settings")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.Run")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.dataloader")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.TextClassificationTrainer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_script")
    def test_runner_language_continuity(self, score_mock, trainer_mock, dataload_mock,
                                        run_mock, parse_mock):
        run_mock.get_context.return_value = MagicMock()
        run_mock.experiment.workspace = "some_workspace"
        parse_mock.return_value = MagicMock()
        parse_mock.return_value.validation_dataset_id = None
        parse_mock.return_value.language = 'some_language'

        dataload_mock.dataset_loader.return_value = "train_set", None, [1, 2, 3]
        trainer_mock.return_value = MagicMock()
        trainer_mock.train.return_value = MagicMock()
        score_mock.return_value = MagicMock()

        run("ignored_input")
        assert dataload_mock.dataset_loader.call_args[0][4] == "some_language"
        assert trainer_mock.call_args[0][1] == "some_language"
