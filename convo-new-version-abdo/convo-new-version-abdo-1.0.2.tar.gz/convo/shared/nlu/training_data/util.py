import json
import logging
import os
import re
from typing import Any, Dict, Optional, Text, Match

from convo.shared.nlu.constants import (
    ENTITIES_NAME,
    EXTRACTOR,
    PRE_TRAINED_EXTRACTORS,
    ATTRIBUTE_START_ENTITY,
    ATTRIBUTE_END_ENTITY,
    ATTRIBUTE_VALUE_ENTITY,
    ATTRIBUTE_TYPE_ENTITY,
    ATTRIBUTE_ROLE_ENTITY,
    ATTRIBUTE_GROUP_ENTITY,
)
from convo.shared.constants import CONVO_UTTER_PREFIX 
import convo.shared.utils.io
import convo.shared.data

log = logging.getLogger(__name__)

ESCAPE_DICT = {"\b": "\\b", "\f": "\\f", "\n": "\\n", "\r": "\\r", "\t": "\\t"}
ESC = re.compile(f'[{"".join(ESCAPE_DICT.values())}]')
UNESCAPE_DICT = {espaced_char: char for char, espaced_char in ESCAPE_DICT.items()}
UNESC = re.compile(f'[{"".join(UNESCAPE_DICT.values())}]')
COMPLETE_MATCH_OF_GROUP = 0


def transforming_entity_synonyms(
    synonyms, known_synonyms: Optional[Dict[Text, Any]] = None
) -> Dict[Text, Any]:
    """Transforms the entity synonyms into a text->value dictionary"""
    entity_name_synonyms = known_synonyms if known_synonyms else {}
    for s in synonyms:
        if "value" in s and "synonyms" in s:
            for synonym in s["synonyms"]:
                entity_name_synonyms[synonym] = s["value"]
    return entity_name_synonyms


def duplicate_synonym_check(
    entity_synonyms: Dict[Text, Any], text: Text, syn: Text, context_str: Text = ""
) -> None:
    if text in entity_synonyms and entity_synonyms[text] != syn:
        convo.shared.utils.io.raising_warning(
            f"Found inconsistent entity synonyms while {context_str}, "
            f"overwriting {text}->{entity_synonyms[text]} "
            f"with {text}->{syn} during merge."
        )


def fetch_file_format_ext(resource_name: Text) -> Text:
    """
    Get the file extension based on training data format. It supports both a folder and
    a file, and tries to guess the format as follows:

    - if the resource is a file and has a known format, return this format's extension
    - if the resource is a folder and all the resources have the
      same known format, return it's extension
    - otherwise, default to DEFAULT_FILE_FORMAT (yml).

    Args:
        resource_name: The name of the resource, can be a file or a folder.
    Returns:
        The resource file format.
    """
    from convo.shared.nlu.training_data import loading

    if resource_name is None or not os.path.exists(resource_name):
        raise AttributeError(f"Resource '{resource_name}' does not exist.")

    filename = convo.shared.utils.io.listing_files(resource_name)

    file_type = list(map(lambda f: loading.guessing_format(f), filename))

    if not file_type:
        return convo.shared.data.convo_yaml_file_extension ()

    file_formats_known = {
        loading.MARKDOWN: convo.shared.data.mark_down_file_extension (),
        loading.CONVO_YAML: convo.shared.data.convo_yaml_file_extension (),
    }
    format = file_type[0]
    if all(f == format for f in file_type):
        return file_formats_known.get(format, convo.shared.data.convo_yaml_file_extension ())

    return convo.shared.data.convo_yaml_file_extension ()


def remove_untrainable_entities(example: Dict[Text, Any]) -> None:
    """Remove untrainable entities from serialised training example `example`.

    Entities with an untrainable extractor will be removed. Untrainable extractors
    are defined in `convo.nlu.constants.PRE_TRAINED_EXTRACTORS`.

    Args:
        example: Serialised training example to inspect.
    """

    exp_entities = example.get(ENTITIES_NAME)

    if not exp_entities:
        # example contains no entities, so there's nothing to do
        return None

    entities_trainable = []

    for entity in exp_entities:
        if entity.get(EXTRACTOR) in PRE_TRAINED_EXTRACTORS:
            log.debug(
                f"Excluding entity '{json.dumps(entity)}' from training data. "
                f"Entity examples extracted by the following classes are not "
                f"dumped to training data in markdown format: "
                f"`{'`, `'.join(sorted(PRE_TRAINED_EXTRACTORS))}`."
            )
        else:
            entities_trainable.append(entity)

    example[ENTITIES_NAME] = entities_trainable


def intents_response_key_to_template_key(intent_response_key: Text) -> Text:
    """Resolve the response template key for a given intent response key.

    Args:
        intent_response_key: retrieval intent with the response key suffix attached.

    Returns: The corresponding response template.

    """
    return f"{CONVO_UTTER_PREFIX }{intent_response_key}"


def template_key_to_intents_response_key(template_key: Text) -> Text:
    """Resolve the intent response key for the given response template.

    Args:
        template_key: Name of the response template.

    Returns: The corresponding intent response key.

    """
    return template_key.split(CONVO_UTTER_PREFIX )[1]


def encode_str(s: Text) -> Text:
    """Return an encoded python string."""

    def change(match: Match) -> Text:
        return ESCAPE_DICT[match.group(COMPLETE_MATCH_OF_GROUP)]

    return ESC.sub(change, s)


def decode_str(s: Text) -> Text:
    """Return a decoded python string."""

    def change(match: Match) -> Text:
        return UNESCAPE_DICT[match.group(COMPLETE_MATCH_OF_GROUP)]

    return UNESC.sub(change, s)


def building_entity(
    start: int,
    end: int,
    value: Text,
    entity_type: Text,
    role: Optional[Text] = None,
    group: Optional[Text] = None,
    **kwargs: Any,
) -> Dict[Text, Any]:
    """Builds a standard entity dictionary.

    Adds additional keyword parameters.

    Args:
        start: start position of entity
        end: end position of entity
        value: text value of the entity
        entity_type: name of the entity type
        role: role of the entity
        group: group of the entity
        **kwargs: additional parameters

    Returns:
        an entity dictionary
    """

    entity_name = {
        ATTRIBUTE_START_ENTITY: start,
        ATTRIBUTE_END_ENTITY: end,
        ATTRIBUTE_VALUE_ENTITY: value,
        ATTRIBUTE_TYPE_ENTITY: entity_type,
    }

    if role:
        entity_name[ATTRIBUTE_ROLE_ENTITY] = role
    if group:
        entity_name[ATTRIBUTE_GROUP_ENTITY] = group

    entity_name.update(kwargs)
    return entity_name
