import logging

from typing import Any, Dict, List, NoReturn, Optional, Text, Tuple, Type
from tqdm import tqdm

import convo.shared.utils.io
from convo.nlu.tokenizers.convert_tokenizer import ConveRTTokenizer
from convo.shared.constants import COMPONENTS_DOCUMENTS_URL
from convo.nlu.tokenizers.tokenizer import Tkn
from convo.nlu.components import Element
from convo.nlu.featurizers.featurizer import CondensedFeaturizer
from convo.shared.nlu.training_data.features import Features
from convo.nlu.config import ConvoNLUModelConfiguration
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
from convo.nlu.constants import (
    DENSE_FEATURE_ATTRS,
    FEATURE_CLASS_AS,
    NAMES_OF_TOKENS,
)
from convo.shared.nlu.constants import TXT, FEATURED_TYPE_SENTENCE, FEATURED_TYPE_SEQUENCE
import numpy as np
import tensorflow as tf

import convo.utils.train_utils as train_utils

log = logging.getLogger(__name__)


class ConveRTFeaturizer(CondensedFeaturizer):
    """Featurizer using ConveRT model.

    Loads the ConveRT(https://github.com/PolyAI-LDN/polyai-models#convert)
    model from TFHub and computes sentence and sequence level feature representations
    for dense featurizable attributes of each message object.
    """

    @classmethod
    def required_components(cls) -> List[Type[Element]]:
        return [ConveRTTokenizer]

    @classmethod
    def required_packages(cls) -> List[Text]:
        return ["tensorflow_text", "tensorflow_hub"]

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:

        super(ConveRTFeaturizer, self).__init__(component_config)

    @staticmethod
    def __fetch_signature(signature: Text, module: Any) -> NoReturn:
        """Retrieve a signature from a (hopefully loaded) TF model."""

        if not module:
            raise Exception(
                "ConveRTFeaturizer needs a proper loaded tensorflow module when used. "
                "Make sure to pass a module when training and using the component."
            )

        return module.signatures[signature]

    def _evaluate_features(
        self, batch_examples: List[Msg], module: Any, attribute: Text = TXT
    ) -> Tuple[np.ndarray, np.ndarray]:

        statement_encodings = self._evaluate_sentence_encodings(
            batch_examples, module, attribute
        )

        (
            sequence_encodings,
            number_of_tokens_in_sentence,
        ) = self._evaluate_sequence_encodings(batch_examples, module, attribute)

        return self._fetch_features(
            statement_encodings, sequence_encodings, number_of_tokens_in_sentence
        )

    def _evaluate_sentence_encodings(
        self, batch_examples: List[Msg], module: Any, attribute: Text = TXT
    ) -> np.ndarray:
        # Get text for attribute of each example
        batch_attribute_txt = [ex.get(attribute) for ex in batch_examples]
        statement_encodings = self._statement_encoding_of_txt(
            batch_attribute_txt, module
        )

        # convert them to a sequence of 1
        return np.reshape(statement_encodings, (len(batch_examples), 1, -1))

    def _evaluate_sequence_encodings(
        self, batch_examples: List[Msg], module: Any, attribute: Text = TXT
    ) -> Tuple[np.ndarray, List[int]]:
        tokens_list = [
            example.get(NAMES_OF_TOKENS[attribute]) for example in batch_examples
        ]

        no_of_tokens_in_statement = [
            len(sent_tokens) for sent_tokens in tokens_list
        ]

        # join the tokens to get a clean text to ensure the sequence length of
        # the returned embeddings from ConveRT matches the length of the tokens
        # (including sub-tokens)
        tokenized_txt = self._tokens_to_txt(tokens_list)
        features_token = self._seq_encoding_of_txt(tokenized_txt, module)

        # ConveRT might split up tokens into sub-tokens
        # take the mean of the sub-token vectors and use that as the token vector
        features_token = train_utils.aligning_token_features(
            tokens_list, features_token
        )

        return features_token, no_of_tokens_in_statement

    @staticmethod
    def _fetch_features(
        sentence_encodings: np.ndarray,
        sequence_encodings: np.ndarray,
        number_of_tokens_in_sentence: List[int],
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Get the sequence and sentence features."""

        statement_embeddings = []
        seq_embeddings = []

        for index in range(len(number_of_tokens_in_sentence)):
            seq_len = number_of_tokens_in_sentence[index]
            seq_encoding = sequence_encodings[index][:seq_len]
            statement_encoding = sentence_encodings[index]

            seq_embeddings.append(seq_encoding)
            statement_embeddings.append(statement_encoding)

        return np.array(seq_embeddings), np.array(statement_embeddings)

    @staticmethod
    def _tokens_to_txt(list_of_tokens: List[List[Tkn]]) -> List[Text]:
        """Convert list of tokens to text.

        Add a whitespace between two tokens if the end value of the first tokens is
        not the same as the end value of the second token."""
        txt = []
        for tokens in list_of_tokens:
            txt = ""
            offset = 0
            for token in tokens:
                if offset != token.start:
                    txt += " "
                txt += token.text

                offset = token.end
            txt.append(txt)

        return txt

    def _statement_encoding_of_txt(self, batch: List[Text], module: Any) -> np.ndarray:
        sign = self.__fetch_signature("default", module)
        return sign(tf.convert_to_tensor(batch))["default"].numpy()

    def _seq_encoding_of_txt(self, batch: List[Text], module: Any) -> np.ndarray:
        signature = self.__fetch_signature("encode_sequence", module)

        return signature(tf.convert_to_tensor(batch))["sequence_encoding"].numpy()

    def train(
        self,
        training_data: TrainingDataSet,
        config: Optional[ConvoNLUModelConfiguration] = None,
        *,
        tf_hub_module: Any = None,
        **kwargs: Any,
    ) -> None:
        if config is not None and config.language != "en":
            convo.shared.utils.io.raising_warning(
                f"Since ``ConveRT`` model is trained only on an english "
                f"corpus of conversations, this featurizer should only be "
                f"used if your training data is in english language. "
                f"However, you are training in '{config.language}'. ",
                docs=COMPONENTS_DOCUMENTS_URL + "#convertfeaturizer",
            )

        batch_dimension = 64

        for attribute in DENSE_FEATURE_ATTRS:

            non_empty_eg = list(
                filter(lambda x: x.get(attribute), training_data.training_examples)
            )

            development_bar = tqdm(
                range(0, len(non_empty_eg), batch_dimension),
                desc=attribute.capitalize() + " batches",
            )
            for batch_start_index in development_bar:
                batch_end_indices = min(
                    batch_start_index + batch_dimension, len(non_empty_eg)
                )

                # Collect batch examples
                batch_eg = non_empty_eg[batch_start_index:batch_end_indices]

                (
                    batch_sequence_features,
                    batch_sentence_features,
                ) = self._evaluate_features(batch_eg, tf_hub_module, attribute)

                self._put_features(
                    batch_eg,
                    batch_sequence_features,
                    batch_sentence_features,
                    attribute,
                )

    def process(
        self, message: Msg, *, tf_hub_module: Any = None, **kwargs: Any
    ) -> None:

        for attribute in DENSE_FEATURE_ATTRS:
            if message.get(attribute):
                seq_features, statement_features = self._evaluate_features(
                    [message], tf_hub_module, attribute=attribute
                )

                self._put_features(
                    [message], seq_features, statement_features, attribute
                )

    def _put_features(
        self,
        examples: List[Msg],
        sequence_features: np.ndarray,
        sentence_features: np.ndarray,
        attribute: Text,
    ) -> None:
        for index, example in enumerate(examples):
            _seq_features = Features(
                sequence_features[index],
                FEATURED_TYPE_SEQUENCE,
                attribute,
                self.component_config[FEATURE_CLASS_AS],
            )
            example.adding_features(_seq_features)

            _statement_features = Features(
                sentence_features[index],
                FEATURED_TYPE_SENTENCE,
                attribute,
                self.component_config[FEATURE_CLASS_AS],
            )
            example.adding_features(_statement_features)
