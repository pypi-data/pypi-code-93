import logging
from collections import defaultdict, OrderedDict
from pathlib import Path

import numpy as np
from typing import Any, Dict, Optional, Text, List, Type, Union

from convo.nlu.tokenizers.spacy_tokenizer import TAG_POS_KEY
from convo.shared.constants import COMPONENTS_DOCUMENTS_URL
from convo.nlu.components import Element
from convo.nlu.tokenizers.tokenizer import Tkn
from convo.nlu.tokenizers.tokenizer import Tokenizer
from convo.nlu.featurizers.featurizer import InfrequentFeaturizer
from convo.shared.nlu.training_data.features import Features
from convo.nlu.config import ConvoNLUModelConfiguration
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
from convo.nlu.constants import NAMES_OF_TOKENS, FEATURE_CLASS_AS
from convo.shared.nlu.constants import TXT, FEATURED_TYPE_SEQUENCE

from convo.nlu.model import Metadataset
import convo.utils.io as io_utils

log = logging.getLogger(__name__)

END_OF_STATEMENT = "EOS"
BEGIN_OF_STATEMENT = "BOS"


class LexicalSyntacticFeaturizer(InfrequentFeaturizer):
    """Creates features for entity extraction.

    Moves with a sliding window over every token in the user message and creates
    features according to the configuration.
    """

    @classmethod
    def required_components(cls) -> List[Type[Element]]:
        return [Tokenizer]

    defaults = {
        # 'features' is [before, word, after] array with before, word,
        # after holding keys about which features to use for each word,
        # for example, 'title' in array before will have the feature
        # "is the preceding word in title case?"
        # POS features require 'SpacyTokenizer'.
        "features": [
            ["low", "title", "upper"],
            ["BOS", "EOS", "low", "upper", "title", "digit"],
            ["low", "title", "upper"],
        ]
    }

    function_dictionary = {
        "low": lambda token: token.text.islower(),
        "title": lambda token: token.text.istitle(),
        "prefix5": lambda token: token.text[:5],
        "prefix2": lambda token: token.text[:2],
        "suffix5": lambda token: token.text[-5:],
        "suffix3": lambda token: token.text[-3:],
        "suffix2": lambda token: token.text[-2:],
        "suffix1": lambda token: token.text[-1:],
        "pos": lambda token: token.data.get(TAG_POS_KEY)
        if TAG_POS_KEY in token.data
        else None,
        "pos2": lambda token: token.data.get(TAG_POS_KEY)[:2]
        if "pos" in token.data
        else None,
        "upper": lambda token: token.text.isupper(),
        "digit": lambda token: token.text.isdigit(),
    }

    def __init__(
        self,
        component_config: Dict[Text, Any],
        feature_to_idx_dict: Optional[Dict[Text, Any]] = None,
    ):
        super().__init__(component_config)

        self.feature_to_idx_dict = feature_to_idx_dict or {}
        self.number_of_features = self._calculate_no_of_features()

    def _calculate_no_of_features(self) -> int:
        return sum(
            [
                len(feature_values.values())
                for feature_values in self.feature_to_idx_dict.values()
            ]
        )

    def train(
        self,
        training_data: TrainingDataSet,
        config: Optional[ConvoNLUModelConfiguration] = None,
        **kwargs: Any,
    ) -> None:
        self.feature_to_idx_dict = self._generate_feature_to_idx_dict(training_data)
        self.number_of_features = self._calculate_no_of_features()

        for example in training_data.training_examples:
            self._generate_sparse_features(example)

    def process(self, message: Msg, **kwargs: Any) -> None:
        self._generate_sparse_features(message)

    def _generate_feature_to_idx_dict(
        self, training_data: TrainingDataSet
    ) -> Dict[Text, Dict[Text, int]]:
        """Create dictionary of all feature values.

        Each feature key, defined in the component configuration, points to
        different feature values and their indices in the overall resulting
        feature vector.
        """

        # get all possible feature values
        every_features = []
        for example in training_data.training_examples:
            lexical_syntactic_featurize_tokens = example.get(NAMES_OF_TOKENS[TXT])
            if lexical_syntactic_featurize_tokens:
                every_features.append(self._features_tokens(lexical_syntactic_featurize_tokens))

        # build vocabulary of features
        feature_vocab = self._build_feature_vocab(every_features)

        # assign a unique index to each feature value
        return self._map_features_to_index(feature_vocab)

    @staticmethod
    def _map_features_to_index(
        feature_vocabulary: Dict[Text, List[Text]]
    ) -> Dict[Text, Dict[Text, int]]:
        feature_to_idx_dictionary = {}
        off_set = 0

        for feature_name, feature_values in feature_vocabulary.items():
            feature_to_idx_dictionary[feature_name] = {
                str(feature_value): feature_idx
                for feature_idx, feature_value in enumerate(
                    sorted(feature_values), start=off_set
                )
            }
            off_set += len(feature_values)

        return feature_to_idx_dictionary

    @staticmethod
    def _build_feature_vocab(
        features: List[List[Dict[Text, Any]]]
    ) -> Dict[Text, List[Text]]:
        feature_vocab = defaultdict(set)

        for sentence_features in features:
            for token_features in sentence_features:
                for feature_name, feature_value in token_features.items():
                    feature_vocab[feature_name].add(feature_value)

        # sort items to ensure same order every time (for tests)
        feature_vocab = OrderedDict(sorted(feature_vocab.items()))

        return feature_vocab

    def _generate_sparse_features(self, message: Msg) -> None:
        """Convert incoming messages into sparse features using the configured
        features."""
        import scipy.sparse

        lexical_syntactic_featurize_tokens = message.get(NAMES_OF_TOKENS[TXT])
        # this check is required because there might be training data examples without TXT,
        # e.g., `Msg("", {action_name: "action_listen"})`
        if lexical_syntactic_featurize_tokens:
            statement_features = self._features_tokens(lexical_syntactic_featurize_tokens)
            one_hot_sequence_feature_vector = self._features_to_hot_one(statement_features)

            seq_features = scipy.sparse.coo_matrix(one_hot_sequence_feature_vector)

            final_seq_features = Features(
                seq_features,
                FEATURED_TYPE_SEQUENCE,
                TXT,
                self.component_config[FEATURE_CLASS_AS],
            )
            message.adding_features(final_seq_features)

    def _features_tokens(self, tokens: List[Tkn]) -> List[Dict[Text, Any]]:
        """Convert words into discrete features."""

        config_features = self.component_config["features"]
        statement_features = []

        for token_idx in range(len(tokens)):
            # get the window size (e.g. before, word, after) of the configured features
            # in case of an even number we will look at one more word before,
            # e.g. window size 4 will result in a window range of
            # [-2, -1, 0, 1] (0 = current word in sentence)
            window_dimension = len(config_features)
            half_window_dimension = window_dimension // 2
            window_scope = range(-half_window_dimension, half_window_dimension + window_dimension % 2)

            affixes = [str(i) for i in window_scope]

            features_token = {}

            for pointer_position in window_scope:
                present_idx = token_idx + pointer_position

                # skip, if present_idx is pointing to a non-existing token
                if present_idx < 0 or present_idx >= len(tokens):
                    continue

                lexical_syntactic_featurize_token = tokens[token_idx + pointer_position]

                present_feature_idx = pointer_position + half_window_dimension
                affix = affixes[present_feature_idx]

                for feature in config_features[present_feature_idx]:
                    features_token[f"{affix}:{feature}"] = self._fetch_feature_value(
                        feature, lexical_syntactic_featurize_token, token_idx, pointer_position, len(tokens)
                    )

            statement_features.append(features_token)

        return statement_features

    def _features_to_hot_one(
        self, sentence_features: List[Dict[Text, Any]]
    ) -> np.ndarray:
        """Convert the word features into a one-hot presentation using the indices
        in the feature-to-idx dictionary."""

        one_hot_sequence_feature_vector = np.zeros(
            [len(sentence_features), self.number_of_features]
        )

        for token_idx, token_features in enumerate(sentence_features):
            for feature_name, feature_value in token_features.items():
                feature_value_string = str(feature_value)
                if (
                    feature_name in self.feature_to_idx_dict
                    and feature_value_string in self.feature_to_idx_dict[feature_name]
                ):
                    idx_features = self.feature_to_idx_dict[feature_name][
                        feature_value_string
                    ]
                    one_hot_sequence_feature_vector[token_idx][idx_features] = 1

        return one_hot_sequence_feature_vector

    def _fetch_feature_value(
        self,
        feature: Text,
        token: Tkn,
        token_idx: int,
        pointer_position: int,
        token_length: int,
    ) -> Union[bool, int, Text]:
        if feature == END_OF_STATEMENT:
            return token_idx + pointer_position == token_length - 1

        if feature == BEGIN_OF_STATEMENT:
            return token_idx + pointer_position == 0

        if feature not in self.function_dictionary:
            raise ValueError(
                f"Configured feature '{feature}' not valid. Please check "
                f"'{COMPONENTS_DOCUMENTS_URL}' for valid configuration parameters."
            )

        val = self.function_dictionary[feature](token)
        if val is None:
            log.debug(
                f"Invalid val '{val}' for feature '{feature}'."
                f" Feature is ignored."
            )
        return val

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional[Metadataset] = None,
        cached_component: Optional["LexicalSyntacticFeaturizer"] = None,
        **kwargs: Any,
    ) -> "LexicalSyntacticFeaturizer":

        filename = meta.get("file")

        feature_to_idx_filename = Path(model_dir) / f"{filename}.feature_to_idx_dict.pkl"
        feature_to_idx_dictionary = io_utils.json_un_pickle(feature_to_idx_filename)

        return LexicalSyntacticFeaturizer(meta, feature_to_idx_dict=feature_to_idx_dictionary)

    def persist(self, filename: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this model into the passed dir.
        Return the metadata necessary to load the model again."""

        feature_to_idx_filename = Path(model_dir) / f"{filename}.feature_to_idx_dict.pkl"
        io_utils.dictionary_pickle(feature_to_idx_filename, self.feature_to_idx_dict)

        return {"file": filename}
