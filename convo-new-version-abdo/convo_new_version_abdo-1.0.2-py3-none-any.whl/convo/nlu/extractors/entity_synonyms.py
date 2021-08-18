import os
from typing import Any, Dict, List, Optional, Text, Type

from convo.nlu.components import Element
from convo.shared.constants import TRAINING_DATA_DOCUMENTS_URL
from convo.shared.nlu.constants import ENTITIES_NAME, TXT
from convo.nlu.config import ConvoNLUModelConfiguration
from convo.nlu.extractors.extractor import ExtractorEntity
from convo.nlu.model import Metadataset
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
from convo.nlu.utils import write_json_to_file
import convo.utils.io
import convo.shared.utils.io


class EntitySynonymMapper(ExtractorEntity):
    @classmethod
    def required_components(cls) -> List[Type[Element]]:
        return [ExtractorEntity]

    def __init__(
        self,
        component_config: Optional[Dict[Text, Any]] = None,
        synonyms: Optional[Dict[Text, Any]] = None,
    ) -> None:

        super().__init__(component_config)

        self.synonyms = synonyms if synonyms else {}

    def train(
        self,
        training_data: TrainingDataSet,
        config: Optional[ConvoNLUModelConfiguration] = None,
        **kwargs: Any,
    ) -> None:

        for key, value in list(training_data.entity_synonyms.items()):
            self.append_entities_if_synonyms(key, value)

        for example in training_data.entity_exp:
            for entity in example.get(ENTITIES_NAME, []):
                entity_value = example.get(TXT)[entity["start"] : entity["end"]]
                self.append_entities_if_synonyms(entity_value, str(entity.get("value")))

    def process(self, message: Msg, **kwargs: Any) -> None:

        upgraded_entities = message.get(ENTITIES_NAME, [])[:]
        self.synonyms_replacement(upgraded_entities)
        message.put(ENTITIES_NAME, upgraded_entities, add_to_output=True)

    def persist(self, filename: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:

        if self.synonyms:
            filename = filename + ".json"
            entity_synonyms_filename = os.path.join(model_dir, filename)
            write_json_to_file(
                entity_synonyms_filename, self.synonyms, separators=(",", ": ")
            )
            return {"file": filename}
        else:
            return {"file": None}

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional[Metadataset] = None,
        cached_component: Optional["EntitySynonymMapper"] = None,
        **kwargs: Any,
    ) -> "EntitySynonymMapper":

        filename = meta.get("file")
        if not filename:
            equivalent = None
            return cls(meta, equivalent)

        entity_synonyms_filename = os.path.join(model_dir, filename)
        if os.path.isfile(entity_synonyms_filename):
            equivalent = convo.shared.utils.io.reading_json_file(entity_synonyms_filename)
        else:
            equivalent = None
            convo.shared.utils.io.raising_warning(
                f"Failed to load synonyms file from '{entity_synonyms_filename}'.",
                docs=TRAINING_DATA_DOCUMENTS_URL + "#synonyms",
            )
        return cls(meta, equivalent)

    def synonyms_replacement(self, entities) -> None:
        for entity in entities:
            # need to wrap in `str` to handle e.g. entity values of type int
            entity_val = str(entity["value"])
            if entity_val.lower() in self.synonyms:
                entity["value"] = self.synonyms[entity_val.lower()]
                self.add_processor_name(entity)

    def append_entities_if_synonyms(self, entity_a, entity_b) -> None:
        if entity_b is not None:
            genuine = str(entity_a)
            substitution = str(entity_b)

            if genuine != substitution:
                genuine = genuine.lower()
                if genuine in self.synonyms and self.synonyms[genuine] != substitution:
                    convo.shared.utils.io.raising_warning(
                        f"Found conflicting synonym definitions "
                        f"for {repr(genuine)}. Overwriting target "
                        f"{repr(self.synonyms[genuine])} with "
                        f"{repr(substitution)}. "
                        f"Check your training data and remove "
                        f"conflicting synonym definitions to "
                        f"prevent this from happening.",
                        docs=TRAINING_DATA_DOCUMENTS_URL + "#synonyms",
                    )

                self.synonyms[genuine] = substitution
