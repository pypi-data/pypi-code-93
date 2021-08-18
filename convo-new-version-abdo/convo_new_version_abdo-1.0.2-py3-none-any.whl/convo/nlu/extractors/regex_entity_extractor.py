import logging
import os
import re
from typing import Any, Dict, List, Optional, Text

import convo.shared.utils.io
import convo.nlu.utils.pattern_utils as pattern_utils
from convo.nlu.model import Metadataset
from convo.nlu.config import ConvoNLUModelConfiguration
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
from convo.shared.nlu.constants import (
    ENTITIES_NAME,
    ATTRIBUTE_VALUE_ENTITY,
    ATTRIBUTE_START_ENTITY,
    ATTRIBUTE_END_ENTITY,
    TXT,
    ATTRIBUTE_TYPE_ENTITY,
)
from convo.nlu.extractors.extractor import ExtractorEntity

log = logging.getLogger(__name__)


class ExtractRegexEntity(ExtractorEntity):
    """Searches for entities in the user's message using the lookup tables and regexes
    defined in the training data."""

    defaults = {
        # text will be processed with case insensitive as default
        "case_sensitive": False,
        # use lookup tables to extract entities
        "use_lookup_tables": True,
        # use regexes to extract entities
        "use_regexes": True,
    }

    def __init__(
        self,
        component_config: Optional[Dict[Text, Any]] = None,
        patterns: Optional[List[Dict[Text, Text]]] = None,
    ):
        super(ExtractRegexEntity, self).__init__(component_config)

        self.case_sensitive = self.component_config["case_sensitive"]
        self.patterns = patterns or []

    def train(
        self,
        training_data: TrainingDataSet,
        config: Optional[ConvoNLUModelConfiguration] = None,
        **kwargs: Any,
    ) -> None:
        self.patterns = pattern_utils.patterns_extract(
            training_data,
            use_lookup_tables=self.component_config["use_lookup_tables"],
            use_regexes=self.component_config["use_regexes"],
            use_only_entities=True,
        )

        if not self.patterns:
            convo.shared.utils.io.raising_warning(
                "No lookup tables or regexes defined in the training data that have "
                "a name equal to any entity in the training data. In order for this "
                "component to work you need to define valid lookup tables or regexes "
                "in the training data."
            )

    def process(self, message: Msg, **kwargs: Any) -> None:
        if not self.patterns:
            return

        withdraw_entities = self._withdraw_entities(message)
        withdraw_entities = self.add_extractor_name(withdraw_entities)

        message.put(
            ENTITIES_NAME, message.get(ENTITIES_NAME, []) + withdraw_entities, add_to_output=True
        )

    def _withdraw_entities(self, message: Msg) -> List[Dict[Text, Any]]:
        """Extract entities of the given type from the given user message."""
        entities = []

        fetch_flags = 0  # default flag
        if not self.case_sensitive:
            fetch_flags = re.IGNORECASE

        for pattern in self.patterns:
            equivalentes = re.finditer(pattern["pattern"], message.get(TXT), flags=fetch_flags)
            equivalentes = list(equivalentes)

            for match in equivalentes:
                start_indices = match.start()
                end_indices = match.end()
                entities.append(
                    {
                        ATTRIBUTE_TYPE_ENTITY: pattern["name"],
                        ATTRIBUTE_START_ENTITY: start_indices,
                        ATTRIBUTE_END_ENTITY: end_indices,
                        ATTRIBUTE_VALUE_ENTITY: message.get(TXT)[
                            start_indices:end_indices
                        ],
                    }
                )

        return entities

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional[Metadataset] = None,
        cached_component: Optional["ExtractRegexEntity"] = None,
        **kwargs: Any,
    ) -> "ExtractRegexEntity":

        filename = meta.get("file")
        regex_filename = os.path.join(model_dir, filename)

        if os.path.exists(regex_filename):
            designs = convo.shared.utils.io.reading_json_file(regex_filename)
            return ExtractRegexEntity(meta, patterns=designs)

        return ExtractRegexEntity(meta)

    def persist(self, filename: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this model into the passed dir.
        Return the metadata necessary to load the model again."""
        filename = f"{filename}.json"
        regex_filename = os.path.join(model_dir, filename)
        convo.shared.utils.io.dump_object_as_json_to_file(regex_filename, self.patterns)

        return {"file": filename}
