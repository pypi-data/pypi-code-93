# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Named entity recognition fine-tuning: utilities to work with CoNLL-2003 task."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


@dataclass
class InputExample:
    """
    A single training/test example for token classification.

    guid: Unique id for the example.
    words: list. The words of the sequence.
    labels: (Optional) list. The labels for each word of the sequence. This should be
    specified for train and dev examples, but not for test examples.
    """
    guid: str
    words: List[str]
    labels: Optional[List[str]]


@dataclass
class InputFeatures:
    """
    A single set of features of data.

    Property names are the same names as the corresponding inputs to a model.
    """
    input_ids: List[int]
    attention_mask: List[int]
    token_type_ids: Optional[List[int]] = None
    label_ids: Optional[List[int]] = None


class Split(Enum):
    """Split Enum Class."""
    train = "train"
    dev = "dev"
    test = "test"


def get_labels(labels_file_path: str) -> List[str]:
    """
    Retrieve labels from saved labels file
    :param labels_file_path:
    :return: list of labels
    """
    """Get labels."""
    if labels_file_path:
        with open(labels_file_path, "r") as f:
            readlines = f.read()
            labels = readlines.splitlines()
        if "O" not in labels:
            labels = ["O"] + labels
        if "" in labels:
            labels.remove("")
        return labels
    else:
        return ["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]
