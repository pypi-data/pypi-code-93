import json
from collections import OrderedDict
from pathlib import Path

import convo.shared.nlu.training_data.util
from convo.shared.constants import INTENT_MSG_PREFIX 

from convo.shared.nlu.constants import (
    INTENTION,
    ATTRIBUTE_VALUE_ENTITY,
    ATTRIBUTE_START_ENTITY,
    ATTRIBUTE_END_ENTITY,
    ATTRIBUTE_TYPE_ENTITY,
    ATTRIBUTE_GROUP_ENTITY,
    ATTRIBUTE_ROLE_ENTITY,
)

import convo.shared.utils.io
import typing
from typing import Text, Dict, Any, Union

if typing.TYPE_CHECKING:
    from convo.shared.nlu.training_data.training_data import TrainingDataSet


class TrainingDataReviewer:
    def __init__(self):
        self.filename: Text = ""

    def reading(self, filename: Union[Text, Path], **kwargs: Any) -> "TrainingDataSet":
        """Reads TrainingDataSet from a file."""
        self.filename = filename
        return self.data_reads(convo.shared.utils.io.read_file(filename), **kwargs)

    def data_reads(self, s: Text, **kwargs: Any) -> "TrainingDataSet":
        """Reads TrainingDataSet from a string."""
        raise NotImplementedError


class TrainingDataAuthor:
    def dump(self, filename: Text, training_data) -> None:
        """Writes a TrainingDataSet object in markdown format to a file."""
        t = self.data_dumps(training_data)
        convo.shared.utils.io.writing_text_file(t, filename)

    def data_dumps(self, training_data: "TrainingDataSet") -> Text:
        """Turns TrainingDataSet into a string."""
        raise NotImplementedError

    @staticmethod
    def preparing_training_exps(training_data: "TrainingDataSet") -> OrderedDict:
        """Pre-processes training data examples by removing not trainable entities."""

        import convo.shared.nlu.training_data.util as convo_nlu_training_data_utils

        training_exps = OrderedDict()

        # Sort by intent while keeping basic intent order
        for example in [e.as_dictionary_nlu() for e in training_data.training_examples]:
            if not example.get(INTENTION):
                continue
            convo_nlu_training_data_utils.remove_untrainable_entities(example)
            intention = example[INTENTION]
            training_exps.setdefault(intention, [])
            training_exps[intention].append(example)

        return training_exps

    @staticmethod
    def generate_list_item(text: Text) -> Text:
        """Generates text for a list item."""

        return f"- {convo.shared.nlu.training_data.util.encode_str(text)}\n"

    @staticmethod
    def generate_msg(message: Dict[Text, Any]) -> Text:
        """Generates text for a message object."""

        md = ""
        text = message.get("text", "")

        position = 0

        # If a message was prefixed with `INTENT_MSG_PREFIX ` (this can only happen
        # in end-to-end stories) then potential entities were provided in the json
        # format (e.g. `/greet{"name": "Convo"}) and we don't have to add the NLU
        # entity annotation
        if not text.startswith(INTENT_MSG_PREFIX ):
            entities = sorted(message.get("entities", []), key=lambda k: k["start"])

            for entity in entities:
                md += text[position : entity["start"]]
                md += TrainingDataAuthor.generating_entity(text, entity)
                position = entity["end"]

        md += text[position:]

        return md

    @staticmethod
    def generating_entity(text: Text, entity: Dict[Text, Any]) -> Text:
        """Generates text for an entity object."""

        entity_text_str = text[
            entity[ATTRIBUTE_START_ENTITY] : entity[ATTRIBUTE_END_ENTITY]
        ]
        types_of_entity = entity.get(ATTRIBUTE_TYPE_ENTITY)
        entity_val = entity.get(ATTRIBUTE_VALUE_ENTITY)
        role_of_entity = entity.get(ATTRIBUTE_ROLE_ENTITY)
        group_of_entity = entity.get(ATTRIBUTE_GROUP_ENTITY)

        if entity_val and entity_val == entity_text_str:
            entity_val = None

        using_short_syntax = (
            entity_val is None and role_of_entity is None and group_of_entity is None
        )

        if using_short_syntax:
            return f"[{entity_text_str}]({types_of_entity})"
        else:
            entity_dictionary = OrderedDict(
                [
                    (ATTRIBUTE_TYPE_ENTITY, types_of_entity),
                    (ATTRIBUTE_ROLE_ENTITY, role_of_entity),
                    (ATTRIBUTE_GROUP_ENTITY, group_of_entity),
                    (ATTRIBUTE_VALUE_ENTITY, entity_val),
                ]
            )
            entity_dictionary = OrderedDict(
                [(k, v) for k, v in entity_dictionary.items() if v is not None]
            )

            return f"[{entity_text_str}]{json.dumps(entity_dictionary)}"


class JsonTrainingDataReviewer(TrainingDataReviewer):
    def data_reads(self, s: Text, **kwargs: Any) -> "TrainingDataSet":
        """Transforms string into json object and passes it on."""
        js = json.loads(s)
        return self.reading_from_json(js, **kwargs)

    def reading_from_json(self, js: Dict[Text, Any], **kwargs: Any) -> "TrainingDataSet":
        """Reads TrainingDataSet from a json object."""
        raise NotImplementedError
