from typing import Any, Optional, Text, List, Type

from convo.nlu.config import ConvoNLUModelConfiguration
from convo.nlu.components import Element
from convo.nlu.featurizers.featurizer import CondensedFeaturizer
from convo.shared.nlu.training_data.features import Features
from convo.nlu.utils.hugging_face.hf_transformers import HF_Transformers_NLP
from convo.nlu.tokenizers.lm_tokenizer import Lang_Model_Tokenizer
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
from convo.nlu.constants import (
    LANG_MODEL_DOCUMENTS,
    DENSE_FEATURE_ATTRS,
    SEQUENTIAL_FEATURES,
    SENTENCE_FTRS,
    FEATURE_CLASS_AS,
)
from convo.shared.nlu.constants import TXT, FEATURED_TYPE_SENTENCE, FEATURED_TYPE_SEQUENCE


class LangModelFeaturizer(CondensedFeaturizer):
    """Featurizer using transformer based language models.

    Uses the output of HF_Transformers_NLP component to set the sequence and sentence
    level representations for dense featurizable attributes of each message object.
    """

    @classmethod
    def required_components(cls) -> List[Type[Element]]:
        return [HF_Transformers_NLP, Lang_Model_Tokenizer]

    def train(
        self,
        training_data: TrainingDataSet,
        config: Optional[ConvoNLUModelConfiguration] = None,
        **kwargs: Any,
    ) -> None:

        for example in training_data.training_examples:
            for attribute in DENSE_FEATURE_ATTRS:
                self._put_lm_features(example, attribute)

    def _fetch_document(self, message: Msg, attribute: Text) -> Any:
        """
        Get the language model doc. A doc consists of
        {'token_ids': ..., 'tokens': ...,
        'sequence_features': ..., 'sentence_features': ...}
        """
        return message.get(LANG_MODEL_DOCUMENTS[attribute])

    def process(self, message: Msg, **kwargs: Any) -> None:
        """Sets the dense features from the language model doc to the incoming
        message."""
        for attribute in DENSE_FEATURE_ATTRS:
            self._put_lm_features(message, attribute)

    def _put_lm_features(self, message: Msg, attribute: Text = TXT) -> None:
        """Adds the precomputed word vectors to the messages features."""
        document = self._fetch_document(message, attribute)

        if document is None:
            return

        seq_features = document[SEQUENTIAL_FEATURES]
        statement_features = document[SENTENCE_FTRS]

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
