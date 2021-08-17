# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utils for selecting requested model and provider given dataset language."""

from azureml.automl.dnn.nlp.classification.common.constants import ModelNames
from azureml.automl.runtime.featurizer.transformer.data.automl_textdnn_provider import AutoMLPretrainedDNNProvider
from azureml.automl.runtime.featurizer.transformer.data.word_embeddings_info import EmbeddingInfo
from typing import Tuple


def get_model_from_language(dataset_language: str, need_path: bool = False) -> Tuple[str, str]:
    """
    return corresponding model name and download path given requested language

    :param dataset_language: user-inputted language from FeaturizationConfig
    :param need_path: whether fetching model provider path is necessary
    """
    if dataset_language.lower() == 'eng':
        model_name = ModelNames.BERT_BASE_CASED
        provider = AutoMLPretrainedDNNProvider(EmbeddingInfo.BERT_BASE_CASED)
    elif dataset_language.lower() == 'deu':
        model_name = ModelNames.BERT_BASE_GERMAN_CASED
        provider = AutoMLPretrainedDNNProvider(EmbeddingInfo.BERT_BASE_GERMAN_CASED_AUTONLP_3_1_0)
    else:
        model_name = ModelNames.BERT_BASE_MULTILINGUAL_CASED
        provider = AutoMLPretrainedDNNProvider(EmbeddingInfo.BERT_BASE_MULTLINGUAL_CASED_AUTONLP_3_1_0)
    return model_name, provider.get_model_dirname() if need_path else ""
