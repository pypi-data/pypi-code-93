import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from azureml.automl.dnn.nlp.classification.io.read.dataloader import _concat_text_and_preserve_label
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import PyTorchMulticlassDatasetWrapper
from azureml.automl.dnn.nlp.classification.multiclass.trainer import TextClassificationTrainer


@pytest.mark.usefixtures('MulticlassDatasetTester')
@pytest.mark.parametrize('multiple_text_column', [True, False])
@pytest.mark.parametrize('include_label_col', [True])
class TestTextClassificationTrainerTests:
    """Tests for Text Classification trainer."""
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoModelForSequenceClassification")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoConfig")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.get_model_from_language")
    def test_train_valid(self, language_mock, trainer_mock, auto_config, auto_tokenizer,
                         auto_model_mock, MulticlassDatasetTester):
        train_df = MulticlassDatasetTester.get_data().copy()
        validation_df = MulticlassDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        train_df = _concat_text_and_preserve_label(train_df, label_column_name)
        validation_df = _concat_text_and_preserve_label(validation_df, label_column_name)
        label_list = pd.unique(train_df[label_column_name])
        training_set = PyTorchMulticlassDatasetWrapper(train_df, label_list, "eng", label_column_name)
        validation_set = PyTorchMulticlassDatasetWrapper(validation_df, label_list, "eng", label_column_name)

        language_mock.return_value = ('some_model_name', "some_model_path")

        auto_config.from_pretrained.return_value = MagicMock()
        auto_tokenizer.from_pretrained.return_value = MagicMock()
        auto_model_mock.from_pretrained.return_value = MagicMock()
        trainer_multiclass = TextClassificationTrainer(label_list, "eng")

        mock_trainer = MagicMock()
        mock_trainer.train.return_value = MagicMock()
        mock_trainer.evaluate.return_value = {"key": "val"}
        trainer_mock.return_value = mock_trainer

        trainer_multiclass.train(training_set)

        # train function
        trainer_multiclass.trainer.train.assert_called_once()
        trainer_multiclass.trainer.save_model.assert_called_once()
        trainer_multiclass.trainer.save_state.assert_called_once()

        # validate function
        results = trainer_multiclass.validate(validation_set)
        trainer_multiclass.trainer.evaluate.assert_called_once()
        assert results is not None
        assert "key" in results.keys()
        assert trainer_multiclass.trainer.log_metrics.call_count == 2
        assert trainer_multiclass.trainer.save_metrics.call_count == 2
        assert auto_config.from_pretrained.call_args[0][0] == 'some_model_name'
        assert auto_tokenizer.from_pretrained.call_args[0][0] == 'some_model_name'
        assert auto_model_mock.from_pretrained.call_args[0][0] == 'some_model_path'
