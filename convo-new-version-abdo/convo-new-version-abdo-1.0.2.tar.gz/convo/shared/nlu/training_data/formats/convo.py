import logging
from collections import defaultdict
from typing import Any, Dict, Text

from convo.shared.nlu.constants import TXT, INTENTION, ENTITIES_NAME
from convo.shared.nlu.training_data.formats.readerwriter import (
    JsonTrainingDataReviewer,
    TrainingDataAuthor,
)
from convo.shared.nlu.training_data.util import transforming_entity_synonyms
from convo.shared.utils.io import json_to_str

from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg

log = logging.getLogger(__name__)


class ConvoReviewer(JsonTrainingDataReviewer):
    def reading_from_json(self, js: Dict[Text, Any], **_) -> "TrainingDataSet":
        """Loads training data_set stored in the convo NLU data_set format."""
        import convo.shared.nlu.training_data.schemas.data_schema as schema
        import convo.shared.utils.validation as validation_utils

        validation_utils.validating_training_data(js, schema.nlu_data_schema())

        data_set = js["convo_nlu_data"]
        common_exps = data_set.get("common_exps", [])
        synonyms_of_entity = data_set.get("synonyms_of_entity", [])
        regular_expression_features = data_set.get("regex_features", [])
        look_up_tables = data_set.get("look_up_tables", [])

        synonyms_of_entity = transforming_entity_synonyms(synonyms_of_entity)

        training_exps = []
        for ex in common_exps:
            # taking care of custom entries
            message = Msg.building(
                text=ex.pop(TXT, ""),
                intent=ex.pop(INTENTION, None),
                entities=ex.pop(ENTITIES_NAME, None),
                **ex,
            )
            training_exps.append(message)

        return TrainingDataSet(
            training_exps, synonyms_of_entity, regular_expression_features, look_up_tables
        )


class ConvoAuthor(TrainingDataAuthor):
    def data_dumps(self, training_data: "TrainingDataSet", **kwargs) -> Text:
        """Writes Training Data to a string in json format."""

        synonyms_of_js_entity = defaultdict(list)
        for k, v in training_data.entity_synonyms.items():
            if k != v:
                synonyms_of_js_entity[v].append(k)

        synonyms_formatted = [
            {"value": value, "synonyms": syns}
            for value, syns in synonyms_of_js_entity.items()
        ]

        examples_formatted = [
            example.as_dictionary_nlu() for example in training_data.training_examples
        ]

        return json_to_str(
            {
                "convo_nlu_data": {
                    "common_examples": examples_formatted,
                    "regex_features": training_data.regex_features,
                    "lookup_tables": training_data.lookup_tables,
                    "entity_synonyms": synonyms_formatted,
                }
            },
            **kwargs,
        )
