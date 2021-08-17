# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2020 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------
""" Finetuning the library models for multi-class classification."""

import logging
import numpy as np
import os
from transformers import (
    AutoConfig,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    default_data_collator,
)
from typing import Any, Dict, List
from azureml._common._error_definition import AzureMLError

from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TextDnnModelDownloadFailed
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.dnn.nlp.classification.common.constants import MultiClassParameters
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import PyTorchMulticlassDatasetWrapper
from azureml.automl.dnn.nlp.classification.multiclass.utils import compute_metrics
from azureml.automl.dnn.nlp.common._model_selector import get_model_from_language
from azureml.automl.dnn.nlp.common.constants import OutputLiterals


logger = logging.getLogger(__name__)


class TextClassificationTrainer:
    """Class to perform training on a text classification model given a dataset"""

    def __init__(self, label_list: List[Any], dataset_language: str):
        """
        Function to initialize text-classification trainer

        :param num_label_cols: Number of unique labels in training set
        """
        self.label_list = label_list
        self.num_labels = len(label_list)
        self.model_name_or_path, download_dir = get_model_from_language(dataset_language, need_path=True)
        if download_dir is None:
            e = AzureMLError.create(TextDnnModelDownloadFailed, transformer='PretrainedBERT',
                                    reference_code=ReferenceCodes._TEXT_DNN_FIT_INITIALIZE,
                                    error_details="BERT CDN failed to download",
                                    target="PretrainedBERTModel")
            raise ClientException._with_error(e)
        config = AutoConfig.from_pretrained(
            self.model_name_or_path,
            num_labels=self.num_labels,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name_or_path,
            use_fast=True,
        )
        # Load model
        self.model = AutoModelForSequenceClassification.from_pretrained(
            download_dir,
            from_tf=False,
            config=config,
        )
        self.trainer = None
        self.training_args = TrainingArguments(
            output_dir=OutputLiterals.OUTPUT_DIR,
            per_device_train_batch_size=MultiClassParameters.TRAIN_BATCH_SIZE,
            per_device_eval_batch_size=MultiClassParameters.VALID_BATCH_SIZE,
            num_train_epochs=MultiClassParameters.EPOCHS,
            save_strategy=MultiClassParameters.SAVE_STRATEGY,
            gradient_accumulation_steps=MultiClassParameters.GRADIENT_ACCUMULATION_STEPS,
        )

        # Padding strategy
        pad_to_max_length = MultiClassParameters.PAD_TO_MAX_LENGTH
        # TODO: look at fp16 when the right time comes
        if pad_to_max_length:
            self.data_collator = default_data_collator
        else:
            self.data_collator = None

    def train(self, train_dataset: PyTorchMulticlassDatasetWrapper):
        """
        Function to perform training on the model given a training dataset

        :param training_set: Datasets.dataset object containing training data
        """
        self.trainer = Trainer(
            model=self.model,
            args=self.training_args,
            train_dataset=train_dataset,
            compute_metrics=compute_metrics,
            tokenizer=self.tokenizer,
            data_collator=self.data_collator,
        )

        train_result = self.trainer.train()
        metrics = train_result.metrics

        self.trainer.save_model()  # Saves the tokenizer too for easy upload
        self.trainer.log_metrics("train", metrics)
        self.trainer.save_metrics("train", metrics)
        self.trainer.save_state()
        if not os.path.exists(OutputLiterals.OUTPUT_DIR):
            os.mkdir(OutputLiterals.OUTPUT_DIR)
        np.save(OutputLiterals.OUTPUT_DIR + '/' + OutputLiterals.LABEL_LIST_FILE_NAME, self.label_list)

    def validate(self, eval_dataset: PyTorchMulticlassDatasetWrapper) -> Dict[str, float]:
        """
        Function to perform evaluate on the model given the trainer object and validation dataset

        :param trainer: Trainer object
        :param validation_set: Datasets.dataset object containing validation data
        """
        logger.info("*** Evaluate ***")
        metrics = self.trainer.evaluate(eval_dataset=eval_dataset)

        self.trainer.log_metrics("eval", metrics)
        self.trainer.save_metrics("eval", metrics)
        return metrics
