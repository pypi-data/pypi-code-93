import os
import typing
from typing import Any, Dict, List, Optional, Text, Type

from convo.nlu.utils.mitie_utils import NLP_Mitie
from convo.nlu.tokenizers.tokenizer import Tokenizer
from convo.nlu.classifiers.classifier import IntentionClassifier
from convo.nlu.components import Element
from convo.nlu.config import ConvoNLUModelConfiguration
from convo.nlu.model import Metadataset
from convo.nlu.constants import NAMES_OF_TOKENS
from convo.shared.nlu.constants import TXT, INTENTION
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg

if typing.TYPE_CHECKING:
    import mitie


class MitieIntentClassifier(IntentionClassifier):
    @classmethod
    def required_components(cls) -> List[Type[Element]]:
        return [NLP_Mitie, Tokenizer]

    def __init__(
        self, component_config: Optional[Dict[Text, Any]] = None, clf=None
    ) -> None:
        """Construct a new intent classifier using the MITIE framework."""

        super().__init__(component_config)

        self.clf = clf

    @classmethod
    def required_packages(cls) -> List[Text]:
        return ["mitie"]

    def train(
        self,
        training_data: TrainingDataSet,
        config: Optional[ConvoNLUModelConfiguration] = None,
        **kwargs: Any,
    ) -> None:
        import mitie

        fetch_model_file = kwargs.get("mitie_file")
        if not fetch_model_file:
            raise Exception(
                "Can not run MITIE entity extractor without a "
                "language model. Make sure this component is "
                "preceeded by the 'NLP_Mitie' component."
            )

        mitie_intent_classifier_trainer = mitie.text_categorizer_trainer(fetch_model_file)
        mitie_intent_classifier_trainer.num_threads = kwargs.get("num_threads", 1)

        for example in training_data.intent_exp:
            mitie_intent_classifier_tokens = self._tokens_of_msg(example)
            mitie_intent_classifier_trainer.add_labeled_text(mitie_intent_classifier_tokens, example.get(INTENTION))

        if training_data.intent_exp:
            # we can not call train if there are no examples!
            self.clf = mitie_intent_classifier_trainer.train()

    def process(self, message: Msg, **kwargs: Any) -> None:

        fetch_mitie_feature = kwargs.get("mitie_feature_extractor")
        if not fetch_mitie_feature:
            raise Exception(
                "Failed to train 'MitieFeaturizer'. "
                "Missing a proper MITIE feature extractor."
            )

        if self.clf:
            token_strings = self._tokens_of_msg(message)
            intentions, confidence = self.clf(token_strings, fetch_mitie_feature)
        else:
            # either the model didn't get trained or it wasn't
            # provided with any data
            intentions = None
            confidence = 0.0

        message.put(
            "intent", {"name": intentions, "confidence": confidence}, add_to_output=True
        )

    @staticmethod
    def _tokens_of_msg(message) -> List[Text]:
        return [token.text for token in message.get(NAMES_OF_TOKENS[TXT], [])]

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional[Metadataset] = None,
        cached_component: Optional["MitieIntentClassifier"] = None,
        **kwargs: Any,
    ) -> "MitieIntentClassifier":
        import mitie

        filename = meta.get("file")

        if not filename:
            return cls(meta)
        get_classifier_file = os.path.join(model_dir, filename)
        if os.path.exists(get_classifier_file):
            data_classifier = mitie.text_categorizer(get_classifier_file)
            return cls(meta, data_classifier)
        else:
            return cls(meta)

    def persist(self, filename: Text, model_dir: Text) -> Dict[Text, Any]:

        if self.clf:
            filename = filename + ".dat"
            get_classifier_file = os.path.join(model_dir, filename)
            self.clf.save_to_disk(get_classifier_file, pure_model=True)
            return {"file": filename}
        else:
            return {"file": None}
