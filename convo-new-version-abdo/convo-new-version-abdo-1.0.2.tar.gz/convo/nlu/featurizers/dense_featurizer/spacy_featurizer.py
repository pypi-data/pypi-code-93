import numpy as np
import typing
import logging
from typing import Any, Optional, Text, Dict, List, Type

from convo.nlu.config import ConvoNLUModelConfiguration
from convo.nlu.components import Element
from convo.nlu.featurizers.featurizer import CondensedFeaturizer
from convo.shared.nlu.training_data.features import Features
from convo.nlu.utils.spacy_utils import SpacyNLP
from convo.nlu.tokenizers.spacy_tokenizer import SpacyTokenizer
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
from convo.nlu.constants import (
    SPACY_DOCUMENTS,
    DENSE_FEATURE_ATTRS,
    FEATURE_CLASS_AS,
)
from convo.shared.nlu.constants import TXT, FEATURED_TYPE_SENTENCE, FEATURED_TYPE_SEQUENCE
from convo.utils.tensorflow.constants import POOL, MEAN_POOL

if typing.TYPE_CHECKING:
    from spacy.tokens import Doc


log = logging.getLogger(__name__)


class SpacyFeaturizer(CondensedFeaturizer):
    @classmethod
    def required_components(cls) -> List[Type[Element]]:
        return [SpacyNLP, SpacyTokenizer]

    defaults = {
        # Specify what pooling operation should be used to calculate the vector of
        # the complete utterance. Available options: 'mean' and 'max'
        POOL: MEAN_POOL
    }

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None):
        super().__init__(component_config)

        self.pooling_operation = self.component_config[POOL]

    def _features_for_document(self, doc: "Doc") -> np.ndarray:
        """Feature vector for a single document / sentence / tokens."""
        return np.array([t.vector for t in doc if t.text and t.text.strip()])

    def train(
        self,
        training_data: TrainingDataSet,
        config: Optional[ConvoNLUModelConfiguration] = None,
        **kwargs: Any,
    ) -> None:

        for example in training_data.training_examples:
            for attribute in DENSE_FEATURE_ATTRS:
                self._put_spacy_features(example, attribute)

    def fetch_doc(self, message: Msg, attribute: Text) -> Any:
        return message.get(SPACY_DOCUMENTS[attribute])

    def process(self, message: Msg, **kwargs: Any) -> None:
        for attribute in DENSE_FEATURE_ATTRS:
            self._put_spacy_features(message, attribute)

    def _put_spacy_features(self, message: Msg, attribute: Text = TXT) -> None:
        """Adds the spacy word vectors to the messages features."""
        document = self.fetch_doc(message, attribute)

        if document is None:
            return

        # in case an empty spaCy model was used, no vectors are present
        if document.vocab.vectors_length == 0:
            log.debug("No features present. You are using an empty spaCy model.")
            return

        seq_features = self._features_for_document(document)
        statement_features = self._calculate_statement_features(
            seq_features, self.pooling_operation
        )

        final_seq_features = Features(
            seq_features,
            FEATURED_TYPE_SEQUENCE,
            attribute,
            self.component_config[FEATURE_CLASS_AS],
        )
        message.adding_features(final_seq_features)
        final_statement_features = Features(
            statement_features,
            FEATURED_TYPE_SENTENCE,
            attribute,
            self.component_config[FEATURE_CLASS_AS],
        )
        message.adding_features(final_statement_features)
