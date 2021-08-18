from typing import Optional, Text, Dict, Any, Union, List, Tuple

import numpy as np

import convo.shared.utils.common
import convo.shared.utils.io
from convo.shared.constants import NEXT_MAJOR_DEPRECATION_VERSION
from convo.nlu.constants import SUB_TOKENS_NUM
from convo.nlu.tokenizers.tokenizer import Tkn
import convo.utils.io as io_utils
from convo.utils.tensorflow.constants import (
    LOSS_CATEGORY,
    SIMILARITY_TYPE_CATEGORY,
    EVALUATE_NUM_EXAMPLES,
    EVALUATE_NUMBER_EPOCHS,
    EPOCHS,
    SOFT_MAX,
    EDGE,
    AUTOMATIC,
    INTERIOR,
    COSINE_VALUE,
)


def normalization(values: np.ndarray, ranking_length: Optional[int] = 0) -> np.ndarray:
    """Normalizes an array of positive numbers over the top `ranking_length` values.
    Other values will be set to 0.
    """

    new_vals = values.copy()  # prevent mutation of the input
    if 0 < ranking_length < len(new_vals):
        classified = sorted(new_vals, reverse=True)
        new_vals[new_vals < classified[ranking_length - 1]] = 0

    if np.sum(new_vals) > 0:
        new_vals = new_vals / np.sum(new_vals)

    return new_vals


def updating_similarity_type(config: Dict[Text, Any]) -> Dict[Text, Any]:
    """
    If SIMILARITY_TYPE_CATEGORY is set to 'auto', update the SIMILARITY_TYPE_CATEGORY depending
    on the LOSS_CATEGORY.
    Args:
        config: model configuration

    Returns: updated model configuration
    """
    if config.get(SIMILARITY_TYPE_CATEGORY) == AUTOMATIC:
        if config[LOSS_CATEGORY] == SOFT_MAX:
            config[SIMILARITY_TYPE_CATEGORY] = INTERIOR
        elif config[LOSS_CATEGORY] == EDGE:
            config[SIMILARITY_TYPE_CATEGORY] = COSINE_VALUE

    return config


def aligning_token_features(
    list_of_tokens: List[List[Tkn]],
    in_token_features: np.ndarray,
    structure: Optional[Tuple] = None,
) -> np.ndarray:
    """Align token features to match tokens.

    ConveRTTokenizer, LanguageModelTokenizers might split up tokens into sub-tokens.
    We need to take the mean of the sub-token vectors and take that as token vector.

    Args:
        list_of_tokens: tokens for examples
        in_token_features: token features from ConveRT
        structure: shape of feature matrix

    Returns:
        Token features.
    """
    if structure is None:
        structure = in_token_features.shape
    output_token_features = np.zeros(structure)

    for example_idx, example_tokens in enumerate(list_of_tokens):
        off_set = 0
        for token_idx, token in enumerate(example_tokens):
            num_sub_words = token.get(SUB_TOKENS_NUM, 1)

            if num_sub_words > 1:
                token_begin_index = token_idx + off_set
                token_last_index = token_idx + off_set + num_sub_words

                mean_vector = np.mean(
                    in_token_features[example_idx][token_begin_index:token_last_index],
                    axis=0,
                )

                off_set += num_sub_words - 1

                output_token_features[example_idx][token_idx] = mean_vector
            else:
                output_token_features[example_idx][token_idx] = in_token_features[
                    example_idx
                ][token_idx + off_set]

    return output_token_features


def updating_evaluation_params(config: Dict[Text, Any]) -> Dict[Text, Any]:
    """
    If EVALUATE_NUMBER_EPOCHS is set to -1, evaluate at the end of the training.

    Args:
        config: model configuration

    Returns: updated model configuration
    """

    if config[EVALUATE_NUMBER_EPOCHS] == -1:
        config[EVALUATE_NUMBER_EPOCHS] = config[EPOCHS]
    elif config[EVALUATE_NUMBER_EPOCHS] < 1:
        raise ValueError(
            f"'{EVALUATE_NUM_EXAMPLES}' is set to "
            f"'{config[EVALUATE_NUMBER_EPOCHS]}'. "
            f"Only values > 1 are allowed for this configuration value."
        )

    return config


def tf_hub_model_loaded(model_url: Text) -> Any:
    """Load model from cache if possible, otherwise from TFHub"""

    import tensorflow_hub as tfhub

    # needed to load the ConveRT model
    # noinspection PyUnresolvedReferences
    import tensorflow_text
    import os

    # required to take care of cases when others files are already
    # stored in the default TFHUB_CACHE_DIR
    try:
        return tfhub.load(model_url)
    except OSError:
        dir = io_utils.create_temp_dir()
        os.environ["TFHUB_CACHE_DIR"] = dir
        return tfhub.load(model_url)


def deprecated_option_replaced(
    old_option: Text,
    new_option: Union[Text, List[Text]],
    config: Dict[Text, Any],
    warn_until_version: Text = NEXT_MAJOR_DEPRECATION_VERSION,
) -> Dict[Text, Any]:
    if old_option in config:
        if isinstance(new_option, str):
            convo.shared.utils.io.rasing_deprecate_warning(
                f"Option '{old_option}' got renamed to '{new_option}'. "
                f"Please update your configuration file.",
                warn_until_version=warn_until_version,
            )
            config[new_option] = config[old_option]
        else:
            convo.shared.utils.io.rasing_deprecate_warning(
                f"Option '{old_option}' got renamed to "
                f"a dictionary '{new_option[0]}' with a key '{new_option[1]}'. "
                f"Please update your configuration file.",
                warn_until_version=warn_until_version,
            )
            option_dictionary = config.get(new_option[0], {})
            option_dictionary[new_option[1]] = config[old_option]
            config[new_option[0]] = option_dictionary

    return config


def validating_deprecated_options(config: Dict[Text, Any]) -> Dict[Text, Any]:
    """
    If old model configuration parameters are present in the provided config, replace
    them with the new parameters and log a warning.
    Args:
        config: model configuration

    Returns: updated model configuration
    """

    # note: call _replace_deprecated_option() here when there are options to deprecate

    return config
