# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Named entity recognition dataset wrapper class."""

from filelock import FileLock
import logging
import os
from typing import List, Optional

import torch
from torch import nn
from torch.utils.data.dataset import Dataset
from transformers import PreTrainedTokenizer

from azureml.automl.dnn.nlp.ner.ner_tasks import convert_examples_to_features, read_examples_from_file
from azureml.automl.dnn.nlp.ner.utils import InputFeatures, Split

logger = logging.getLogger(__name__)


class DatasetWrapper(Dataset):
    """This will be superseded by a framework-agnostic approach soon."""

    features: List[InputFeatures]
    pad_token_label_id: int = nn.CrossEntropyLoss().ignore_index
    # Use cross entropy ignore_index as padding label id so that only
    # real label ids contribute to the loss later.

    def __init__(
            self,
            data_dir: str,
            dataset_file: str,
            tokenizer: PreTrainedTokenizer,
            labels: List[str],
            model_type: str,
            max_seq_length: Optional[int] = None,
            overwrite_cache=False,
            mode: Split = Split.train
    ):
        """Token classification dataset constructor func."""
        # Load data features from cache or dataset file
        cached_features_file = os.path.join(
            data_dir,
            "cached_{}_{}_{}".format(mode.value, tokenizer.__class__.__name__, str(max_seq_length)),
        )
        dataset_path = os.path.join(data_dir, dataset_file)

        # Make sure only the first process in distributed training processes the dataset,
        # and the others will use the cache.
        lock_path = cached_features_file + ".lock"
        with FileLock(lock_path):

            if os.path.exists(cached_features_file) and not overwrite_cache:
                logger.info("Loading features from cached file {}".format(cached_features_file))
                self.features = torch.load(cached_features_file)
            else:
                logger.info("Creating features from dataset file at {}".format(data_dir))
                examples = read_examples_from_file(dataset_path, mode)
                # TODO clean up all this to leverage built-in features of tokenizers
                self.features = convert_examples_to_features(
                    examples,
                    labels,
                    max_seq_length,
                    tokenizer,
                    cls_token_at_end=bool(model_type in ["xlnet"]),
                    # xlnet has a cls token at the end
                    cls_token=tokenizer.cls_token,
                    cls_token_segment_id=2 if model_type in ["xlnet"] else 0,
                    sep_token=tokenizer.sep_token,
                    sep_token_extra=False,
                    # roberta uses an extra separator b/w pairs of sentences
                    # cf. github.com/pytorch/fairseq/commit/1684e166e3da03f5b600dbb7855cb98ddfcd0805
                    pad_on_left=bool(tokenizer.padding_side == "left"),
                    pad_token=tokenizer.pad_token_id,
                    pad_token_segment_id=tokenizer.pad_token_type_id,
                    pad_token_label_id=self.pad_token_label_id,
                )
                logger.info("Saving features into cached file {}".format(cached_features_file))
                torch.save(self.features, cached_features_file)

    def __len__(self):
        """Token classification dataset len func."""
        return len(self.features)

    def __getitem__(self, i) -> InputFeatures:
        """Token classification dataset getitem func."""
        return self.features[i]
