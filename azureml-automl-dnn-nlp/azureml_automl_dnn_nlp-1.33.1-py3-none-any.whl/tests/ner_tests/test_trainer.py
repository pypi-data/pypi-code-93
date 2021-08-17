import pytest
import unittest
from unittest.mock import MagicMock, patch

from azureml.automl.core.shared.exceptions import ValidationException
from azureml.automl.dnn.nlp.common.constants import OutputLiterals
from azureml.automl.dnn.nlp.ner.trainer import NERPytorchTrainer

from ..mocks import ner_trainer_mock


@pytest.mark.usefixtures('new_clean_dir')
class NERTrainerTests(unittest.TestCase):
    """Tests for NER trainer."""

    @patch("azureml.automl.dnn.nlp.ner.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoModelForTokenClassification")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoMLPretrainedDNNProvider")
    def test_train_valid(
            self,
            provider_mock,
            model_mock,
            trainer_mock
    ):
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

        # prepare input params for trainer
        train_dataset = MagicMock()
        eval_dataset = MagicMock()
        label_list = ["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]
        output_dir = OutputLiterals.OUTPUT_DIR
        trainer = NERPytorchTrainer(
            label_list,
            output_dir
        )

        # train
        trainer.train(train_dataset)
        trainer.trainer.train.assert_called_once()
        trainer.trainer.save_model.assert_called_once()
        trainer.trainer.log_metrics.assert_called_once()
        trainer.trainer.save_metrics.assert_called_once()
        trainer.trainer.save_state.assert_called_once()

        # valid
        results = trainer.validate(eval_dataset)
        trainer.trainer.evaluate.assert_called_once()
        assert trainer.trainer.log_metrics.call_count == 2
        assert trainer.trainer.save_metrics.call_count == 2
        assert results is not None
        assert results.get("eval_accuracy")

    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoModelForTokenClassification")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoMLPretrainedDNNProvider")
    def test_validation_without_train(
            self,
            provider_mock,
            model_mock
    ):
        # provider mock
        provider = MagicMock()
        provider.get_model_dirname.return_value = "data/bert-base-cased"
        provider_mock.return_value = provider

        # model mock
        model = MagicMock()
        model.from_pretrained.return_value = MagicMock()
        model_mock.return_value = model

        # prepare input params
        eval_dataset = MagicMock()
        label_list = ["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]
        output_dir = OutputLiterals.OUTPUT_DIR
        trainer = NERPytorchTrainer(
            label_list,
            output_dir
        )

        with self.assertRaises(ValidationException):
            trainer.validate(eval_dataset)

        assert trainer.trainer is None
