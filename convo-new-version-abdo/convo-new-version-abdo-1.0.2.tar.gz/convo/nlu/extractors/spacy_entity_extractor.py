import typing
from typing import Any, Dict, List, Text, Optional, Type

from convo.shared.nlu.constants import ENTITIES_NAME, TXT
from convo.nlu.utils.spacy_utils import SpacyNLP
from convo.nlu.components import Element
from convo.nlu.extractors.extractor import ExtractorEntity
from convo.shared.nlu.training_data.message import Msg

if typing.TYPE_CHECKING:
    from spacy.tokens.doc import Doc  # pytype: disable=import-error


class SpacyEntityExtractor(ExtractorEntity):
    @classmethod
    def required_components(cls) -> List[Type[Element]]:
        return [SpacyNLP]

    defaults = {
        # by default all dimensions recognized by spacy are returned
        # dimensions can be configured to contain an array of strings
        # with the names of the dimensions to filter for
        "dimensions": None
    }

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super().__init__(component_config)

    def process(self, message: Msg, **kwargs: Any) -> None:
        # can't use the existing doc here (spacy_doc on the message)
        # because tokens are lower cased which is bad for NER
        nlp_spacy = kwargs.get("spacy_nlp", None)
        document = nlp_spacy(message.get(TXT))
        all_withdraw = self.add_extractor_name(self.withdraw_entities(document))
        measurements = self.component_config["dimensions"]
        withdraw = SpacyEntityExtractor.filter_irrelevant_entities(
            all_withdraw, measurements
        )
        message.put(ENTITIES_NAME, message.get(ENTITIES_NAME, []) + withdraw, add_to_output=True)

    @staticmethod
    def withdraw_entities(doc: "Doc") -> List[Dict[Text, Any]]:
        entities = [
            {
                "entity": ent.label_,
                "value": ent.text,
                "start": ent.start_char,
                "confidence": None,
                "end": ent.end_char,
            }
            for ent in doc.ents
        ]
        return entities
