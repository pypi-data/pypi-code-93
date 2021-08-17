# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Fine-tuning the library models for named entity recognition in CoNLL-2003 format."""
import logging
from typing import Any, Dict, List

from torch.utils.data import Dataset
from transformers import (
    AutoConfig,
    AutoModelForTokenClassification,
    Trainer,
    TrainingArguments,
)

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ExecutionFailure
from azureml.automl.core.shared.exceptions import ClientException, ValidationException
from azureml.automl.dnn.nlp.common.constants import NERModelParameters
from azureml.automl.dnn.nlp.ner.token_classification_metrics import TokenClassificationMetrics
from azureml.automl.runtime.featurizer.transformer.data.automl_textdnn_provider import AutoMLPretrainedDNNProvider
from azureml.automl.runtime.featurizer.transformer.data.word_embeddings_info import EmbeddingInfo

logger = logging.getLogger(__name__)


class NERPytorchTrainer:
    """Class for training an NER model for a given dataset."""
    def __init__(
            self,
            label_list: List[str],
            output_dir: str,
    ):
        """
        Function to initialize pytorch ner trainer

        :param label_list: list of unique labels
        :param output_dir: output directory to save results to
        """
        self.model_name = NERModelParameters.MODEL_NAME
        self.output_dir = output_dir

        self.label_list = label_list
        num_labels = len(label_list)

        # Load config
        config = AutoConfig.from_pretrained(
            NERModelParameters.MODEL_NAME,
            num_labels=num_labels,
            finetuning_task=NERModelParameters.TASK_NAME
        )

        # Download model from CDN
        provider = AutoMLPretrainedDNNProvider(EmbeddingInfo.BERT_BASE_CASED)
        download_dir = provider.get_model_dirname()
        if download_dir is None:
            raise ClientException('CDN could not be downloaded', has_pii=False)

        # Load model
        self.model = AutoModelForTokenClassification.from_pretrained(
            download_dir,
            from_tf=False,
            config=config
        )

        self.trainer = None

    def train(
            self,
            train_dataset: Dataset
    ) -> None:
        """
        Function to perform training on the model given a training dataset.
        :param train_dataset: dataset to train with
        :return:
        """
        with log_utils.log_activity(
                logger,
                activity_name=constants.TelemetryConstants.TRAINING
        ):
            # Create trainer
            token_classification_metrics = TokenClassificationMetrics(self.label_list)
            training_args = TrainingArguments(
                output_dir=self.output_dir,
                per_device_train_batch_size=NERModelParameters.PER_DEVICE_TRAIN_BATCH_SIZE,
                num_train_epochs=NERModelParameters.NUM_TRAIN_EPOCHS,
                save_steps=NERModelParameters.SAVE_STEPS
            )
            self.trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=train_dataset,
                compute_metrics=token_classification_metrics.compute_metrics
            )

            # Train
            train_result = self.trainer.train()

            # Save model
            self.trainer.save_model()

            # Get metrics info for train data
            metrics = train_result.metrics
            metrics["train_samples"] = len(train_dataset)
            self.trainer.log_metrics("train", metrics)
            self.trainer.save_metrics("train", metrics)
            self.trainer.save_state()

    def validate(
            self,
            eval_dataset: Dataset
    ) -> Dict[str, Any]:
        """
        Function to perform evaluation on the trained model given a val dataset.
        :param eval_dataset: dataset to validate the model with
        :return:
        """
        if self.trainer is None:
            logger.error("Unable to validate when model has not been trained. Please train the model first.")
            raise ValidationException._with_error(
                AzureMLError.create(
                    ExecutionFailure,
                    operation_name="validate",
                    error_details="need to train before calling to validate"
                )
            )

        with log_utils.log_activity(
                logger,
                activity_name=constants.TelemetryConstants.VALIDATION
        ):
            metrics = self.trainer.evaluate(eval_dataset)
            metrics["eval_samples"] = len(eval_dataset)
            self.trainer.log_metrics("eval", metrics)
            self.trainer.save_metrics("eval", metrics)
        return metrics
