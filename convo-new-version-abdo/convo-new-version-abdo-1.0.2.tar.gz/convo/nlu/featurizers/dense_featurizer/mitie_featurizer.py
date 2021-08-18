import numpy as np
import typing
from typing import Any, List, Text, Optional, Dict, Type, Tuple

from convo.nlu.config import ConvoNLUModelConfiguration
from convo.nlu.components import Element
from convo.nlu.featurizers.featurizer import CondensedFeaturizer
from convo.shared.nlu.training_data.features import Features
from convo.nlu.tokenizers.tokenizer import Tkn, Tokenizer
from convo.nlu.utils.mitie_utils import NLP_Mitie
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
from convo.nlu.constants import (
    DENSE_FEATURE_ATTRS,
    FEATURE_CLASS_AS,
    NAMES_OF_TOKENS,
)
from convo.shared.nlu.constants import TXT, FEATURED_TYPE_SENTENCE, FEATURED_TYPE_SEQUENCE
from convo.utils.tensorflow.constants import MEAN_POOL, POOL

if typing.TYPE_CHECKING:
    import mitie


class MitieFeaturizer(CondensedFeaturizer):
    @classmethod
    def required_components(cls) -> List[Type[Element]]:
        return [NLP_Mitie, Tokenizer]

    defaults = {
        # Specify what pooling operation should be used to calculate the vector of
        # the complete utterance. Available options: 'mean' and 'max'
        POOL: MEAN_POOL
    }

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super().__init__(component_config)

        self.pooling_operation = self.component_config["pooling"]

    @classmethod
    def required_packages(cls) -> List[Text]:
        return ["mitie", "numpy"]

    def ndim(self, feature_extractor: "mitie.total_word_feature_extractor") -> int:
        return feature_extractor.num_dimensions

    def train(
        self,
        training_data: TrainingDataSet,
        config: Optional[ConvoNLUModelConfiguration] = None,
        **kwargs: Any,
    ) -> None:

        extractor_mitie_feature = self._extractor_mitie_feature(**kwargs)
        for example in training_data.training_examples:
            for attribute in DENSE_FEATURE_ATTRS:
                self.process_training_eg(
                    example, attribute, extractor_mitie_feature
                )

    def process_training_eg(
        self, example: Msg, attribute: Text, mitie_feature_extractor: Any
    ):
        mitie_featurizer_tokens = example.get(NAMES_OF_TOKENS[attribute])

        if mitie_featurizer_tokens is not None:
            seq_features, statement_features = self.tokens_of_features(
                mitie_featurizer_tokens, mitie_feature_extractor
            )

            self._put_features(example, seq_features, statement_features, attribute)

    def process(self, message: Msg, **kwargs: Any) -> None:
        mitie_feature_extractor = self._extractor_mitie_feature(**kwargs)
        for attribute in DENSE_FEATURE_ATTRS:
            tokens = message.get(NAMES_OF_TOKENS[attribute])
            if tokens:
                seq_features, statement_features = self.tokens_of_features(
                    tokens, mitie_feature_extractor
                )

                self._put_features(
                    message, seq_features, statement_features, attribute
                )

    def _put_features(
        self,
        message: Msg,
        sequence_features: np.ndarray,
        sentence_features: np.ndarray,
        attribute: Text,
    ):
        final_seq_features = Features(
            sequence_features,
            FEATURED_TYPE_SEQUENCE,
            attribute,
            self.component_config[FEATURE_CLASS_AS],
        )
        message.adding_features(final_seq_features)

        final_statement_features = Features(
            sentence_features,
            FEATURED_TYPE_SENTENCE,
            attribute,
            self.component_config[FEATURE_CLASS_AS],
        )
        message.adding_features(final_statement_features)

    def _extractor_mitie_feature(self, **kwargs) -> Any:
        extractor_mitie_feature = kwargs.get("mitie_feature_extractor")
        if not extractor_mitie_feature:
            raise Exception(
                "Failed to train 'MitieFeaturizer'. "
                "Missing a proper MITIE feature extractor. "
                "Make sure this component is preceded by "
                "the 'NLP_Mitie' component in the pipeline "
                "configuration."
            )
        return extractor_mitie_feature

    def tokens_of_features(
        self,
        tokens: List[Tkn],
        feature_extractor: "mitie.total_word_feature_extractor",
    ) -> Tuple[np.ndarray, np.ndarray]:
        # calculate features
        seq_features = []
        for token in tokens:
            seq_features.append(feature_extractor.get_feature_vector(token.text))
        seq_features = np.array(seq_features)

        sentence_fetaures = self._calculate_statement_features(
            seq_features, self.pooling_operation
        )

        return seq_features, sentence_fetaures
