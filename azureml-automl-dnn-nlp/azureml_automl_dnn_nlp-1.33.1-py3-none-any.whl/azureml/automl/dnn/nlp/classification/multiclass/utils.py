# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utility functions for multi-class classification."""

import numpy as np
from transformers import AutoTokenizer, EvalPrediction
from typing import Any, Dict, List, Union
from azureml.automl.dnn.nlp.classification.common.constants import DatasetLiterals


def compute_metrics(p: EvalPrediction):
    """
    Function to compute metrics like accuracy

    :param p: EvalPrediction type dataset comprising of predictions and label_ids
    """
    preds = p.predictions[0] if isinstance(p.predictions, tuple) else p.predictions
    preds = np.argmax(preds, axis=1)
    return {"accuracy": (preds == p.label_ids).astype(np.float32).mean().item()}


def preprocess_function(examples: Union[Dict, List[Any]], tokenizer: AutoTokenizer,
                        padding: str, max_seq_length: int, label_to_id: Union[Dict, None],
                        label_column_name: Union[str, None]) -> Union[Dict, Any]:
    """
    Preprocess the input examples including tokenization of text

    :param examples: input examples belonging to train or validation datasets
    :param tokenizer: the tokenizer corresponding to the pretrained model used for finetuning
    :param padding: type of padding to use
    :param max_seq_length: maximum length of text sequences processed by model
    :param label_to_id: dictionary with label to id mapping
    """
    args = (examples[DatasetLiterals.TEXT_COLUMN],)
    result = tokenizer(*args, padding=padding, max_length=max_seq_length, truncation=True)

    # Only applicable to training, and not to inference
    # Please note that the actual column name for labels in the PyTorch Dataset will remain as "labels"
    # because the DNN forward function (such as that for BERT) only allows for a parameter called "labels"
    if label_column_name is not None and label_to_id is not None and label_column_name in examples:
        result[DatasetLiterals.LABEL_COLUMN] =\
            [(label_to_id[label] if label != -1 else -1) for label in examples[label_column_name]]
    return result
