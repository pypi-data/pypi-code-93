import logging
import os
from typing import Any, Dict, Optional, Text, List, Tuple

import convo.shared.nlu.training_data.util
from convo.shared.constants import DOCUMENTS_BASE_URL
from convo.shared.nlu.training_data.formats.readerwriter import TrainingDataReviewer
from convo.shared.nlu.training_data.util import transforming_entity_synonyms
import convo.shared.utils.io

from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg

log = logging.getLogger(__name__)

DOCUMENTS_URL_MIGRATE_GOOGLE = DOCUMENTS_BASE_URL + "/migrate-from/google-dialogflow-to-convo/"

PACKAGE_DIALOGFLOW = "dialogflow_package"
AGENT_DIALOGFLOW = "dialogflow_agent"
INTENT_DIALOGFLOW = "dialogflow_intent"
EXAMPLES_DIALOGFLOW_INTENT = "dialogflow_intent_examples"
ENTITIES_DIALOGFLOW = "dialogflow_entities"
ENTRIES_DIALOGFLOW_ENTITY = "dialogflow_entity_entries"


class DialogflowReviewer(TrainingDataReviewer):
    def reading(self, fn: Text, **kwargs: Any) -> "TrainingDataSet":
        """Loads training data stored in the Dialogflow data format."""
        lang = kwargs["lang"]
        format = kwargs["format"]

        if format not in {INTENT_DIALOGFLOW, ENTITIES_DIALOGFLOW}:
            raise ValueError(
                "format must be either {}, or {}"
                "".format(INTENT_DIALOGFLOW, ENTITIES_DIALOGFLOW)
            )

        base_js = convo.shared.utils.io.reading_json_file(fn)
        eg_js = self.reading_examples_js(fn, lang, format)

        if not eg_js:
            convo.shared.utils.io.raising_warning(
                f"No training examples found for dialogflow file {fn}!",
                docs=DOCUMENTS_URL_MIGRATE_GOOGLE,
            )
            return TrainingDataSet()
        elif format == INTENT_DIALOGFLOW:
            return self.reading_intent(base_js, eg_js)
        else:  # path for ENTITIES_DIALOGFLOW
            return self.reading_entities(base_js, eg_js)

    def reading_intent(
        self, intent_js: Dict[Text, Any], examples_js: List[Dict[Text, Any]]
    ) -> "TrainingDataSet":
        """Reads the intent and examples from respective jsons."""
        intention = intent_js.get("name")

        training_exps = []
        for ex in examples_js:
            text, entities = self.joining_text_chunks(ex["data"])
            training_exps.append(Msg.building(text, intention, entities))

        return TrainingDataSet(training_exps)

    def joining_text_chunks(
        self, chunks: List[Dict[Text, Any]]
    ) -> Tuple[Text, List[Dict[Text, Any]]]:
        """Combines text chunks and extracts entities."""

        change = ""
        entities = []
        for chunk in chunks:
            entity_name = self.extracting_entity(chunk, len(change))
            if entity_name:
                entities.append(entity_name)
            change += chunk["text"]

        return change, entities

    @staticmethod
    def extracting_entity(
        chunk: Dict[Text, Any], current_offset: int
    ) -> Optional[Dict[Text, Any]]:
        """Extract an entity from a chunk if present."""

        entity_name = None
        if "meta" in chunk or "alias" in chunk:
            begin = current_offset
            text = chunk["text"]
            last = begin + len(text)
            types_of_entity = chunk.get("alias", chunk["meta"])
            if types_of_entity != "@sys.ignore":
                entity_name = convo.shared.nlu.training_data.util.building_entity(
                    begin, last, text, types_of_entity
                )

        return entity_name

    @staticmethod
    def flatten(list_of_lists: List[List[Any]]) -> List[Any]:
        return [item for items in list_of_lists for item in items]

    @staticmethod
    def extracting_lookup_tables(
        name: Text, examples: List[Dict[Text, Any]]
    ) -> Optional[List[Dict[Text, Any]]]:
        """Extract the lookup table from the entity synonyms"""
        other_word = [e["synonyms"] for e in examples if "synonyms" in e]
        other_word = DialogflowReviewer.flatten(other_word)
        component = [synonym for synonym in other_word if "@" not in synonym]

        if len(component) == 0:
            return None
        return [{"name": name, "elements": component}]

    @staticmethod
    def reading_entities(entity_js, examples_js) -> "TrainingDataSet":
        synonyms_entity = transforming_entity_synonyms(examples_js)

        fetch_name = entity_js.get("name")
        look_up_tables = DialogflowReviewer.extracting_lookup_tables(fetch_name, examples_js)
        return TrainingDataSet([], synonyms_entity, [], look_up_tables)

    @staticmethod
    def reading_examples_js(fn: Text, language: Text, fformat: Text) -> Any:
        """Infer and load the example file based on the root
        filename and root format."""

        if fformat == INTENT_DIALOGFLOW:
            type_of_examples = "usersays"
        else:
            type_of_examples = "entries"
        eg_fn_ending = f"_{type_of_examples}_{language}.json"
        eg_fn = fn.replace(".json", eg_fn_ending)
        if os.path.isfile(eg_fn):
            return convo.shared.utils.io.reading_json_file(eg_fn)
        else:
            return None

    def data_reads(self, s, **kwargs):
        raise NotImplementedError
