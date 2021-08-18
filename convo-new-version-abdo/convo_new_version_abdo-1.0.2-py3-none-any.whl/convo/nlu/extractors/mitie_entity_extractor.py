import logging
import os
import typing
from typing import Any, Dict, List, Optional, Text, Type

from convo.nlu.constants import NAMES_OF_TOKENS
from convo.shared.nlu.constants import TXT, ENTITIES_NAME
from convo.nlu.config import ConvoNLUModelConfiguration
from convo.nlu.utils.mitie_utils import NLP_Mitie
from convo.nlu.tokenizers.tokenizer import Tkn, Tokenizer
from convo.nlu.components import Element
from convo.nlu.extractors.extractor import ExtractorEntity
from convo.nlu.model import Metadataset
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
import convo.shared.utils.io

log = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    import mitie


class MitieEntityExtractor(ExtractorEntity):
    @classmethod
    def required_components(cls) -> List[Type[Element]]:
        return [NLP_Mitie, Tokenizer]

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None, ner=None):
        """Construct a new intent classifier using the sklearn framework."""

        super().__init__(component_config)
        self.ner = ner

    @classmethod
    def required_packages(cls) -> List[Text]:
        return ["mitie"]

    def withdraw_entities(
        self, text: Text, tokens: List[Tkn], feature_extractor
    ) -> List[Dict[Text, Any]]:
        entities = []
        tokens_strings = [token.text for token in tokens]
        if self.ner:
            entities = self.ner.fetch_entities(tokens_strings, feature_extractor)
            for e in entities:
                if len(e[0]):
                    begin = tokens[e[0][0]].start
                    stop = tokens[e[0][-1]].end

                    entities.append(
                        {
                            "entity": e[1],
                            "value": text[begin:stop],
                            "start": begin,
                            "end": stop,
                            "confidence": None,
                        }
                    )

        return entities

    def train(
        self,
        training_data: TrainingDataSet,
        config: Optional[ConvoNLUModelConfiguration] = None,
        **kwargs: Any,
    ) -> None:
        import mitie

        model_filename = kwargs.get("mitie_file")
        if not model_filename:
            raise Exception(
                "Can not run MITIE entity extractor without a "
                "language model. Make sure this component is "
                "preceeded by the 'NLP_Mitie' component."
            )

        data_trainer = mitie.ner_trainer(model_filename)
        data_trainer.num_threads = kwargs.get("num_threads", 1)
        got_one_entity = False

        # filter out pre-trained entity examples
        filtered_entity_eg = self.filter_trainable_entities(
            training_data.nlu_exp
        )

        for example in filtered_entity_eg:
            specimen = self._arrange_mitie_sample(example)

            got_one_entity = specimen.num_entities > 0 or got_one_entity
            data_trainer.add(specimen)

        # Mitie will fail to train if there is not a single entity tagged
        if got_one_entity:
            self.ner = data_trainer.training()

    @staticmethod
    def _arrange_mitie_sample(training_example: Msg) -> Any:
        import mitie

        txt = training_example.get(TXT)
        mitie_entity_extractor_tokens = training_example.get(NAMES_OF_TOKENS[TEXT])
        specimen = mitie.ner_training_instance([t.text for t in mitie_entity_extractor_tokens])
        for ent in training_example.get(ENTITIES_NAME, []):
            try:
                # if the token is not aligned an exception will be raised
                begin, stop = MitieEntityExtractor.find_entity(ent, txt, mitie_entity_extractor_tokens)
            except ValueError as e:
                convo.shared.utils.io.raising_warning(
                    f"Failed to use example '{txt}' to train MITIE "
                    f"entity extractor. Example will be skipped."
                    f"Error: {e}"
                )
                continue
            try:
                # mitie will raise an exception on malicious
                # input - e.g. on overlapping entities
                specimen.add_entity(list(range(begin, stop)), ent["entity"])
            except Exception as e:
                convo.shared.utils.io.raising_warning(
                    f"Failed to add entity example "
                    f"'{str(e)}' of sentence '{str(txt)}'. "
                    f"Example will be ignored. Reason: "
                    f"{e}"
                )
                continue
        return specimen

    def process(self, message: Msg, **kwargs: Any) -> None:

        extractor_mitie_feature = kwargs.get("mitie_feature_extractor")
        if not extractor_mitie_feature:
            raise Exception(
                "Failed to train 'MitieFeaturizer'. "
                "Missing a proper MITIE feature extractor."
            )

        ents = self.withdraw_entities(
            message.get(TXT), message.get(NAMES_OF_TOKENS[TXT]), extractor_mitie_feature
        )
        withdraw = self.add_extractor_name(ents)
        message.put(ENTITIES_NAME, message.get(ENTITIES_NAME, []) + withdraw, add_to_output=True)

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Text = None,
        model_metadata: Metadataset = None,
        cached_component: Optional["MitieEntityExtractor"] = None,
        **kwargs: Any,
    ) -> "MitieEntityExtractor":
        import mitie

        filename = meta.get("file")

        if not filename:
            return cls(meta)

        file_classifier = os.path.join(model_dir, filename)
        if os.path.exists(file_classifier):
            extract = mitie.named_entity_extractor(file_classifier)
            return cls(meta, extract)
        else:
            return cls(meta)

    def persist(self, filename: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:

        if self.ner:
            filename = filename + ".dat"
            entity_file_extractor = os.path.join(model_dir, filename)
            self.ner.save_to_disk(entity_file_extractor, pure_model=True)
            return {"file": filename}
        else:
            return {"file": None}
