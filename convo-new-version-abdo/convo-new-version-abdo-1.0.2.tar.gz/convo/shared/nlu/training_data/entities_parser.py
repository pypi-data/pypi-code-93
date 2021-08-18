import re
from json import JSONDecodeError
from typing import Text, List, Dict, Match, Optional, NamedTuple, Any

import convo.shared.nlu.training_data.util
from convo.shared.constants import TRAINING_DATA_NLU_DOCUMENTS_URL
from convo.shared.nlu.constants import (
    ATTRIBUTE_VALUE_ENTITY,
    ATTRIBUTE_TYPE_ENTITY,
    ATTRIBUTE_GROUP_ENTITY,
    ATTRIBUTE_ROLE_ENTITY,
)
from convo.shared.nlu.training_data.message import Msg
import convo.shared.utils.io

ENTITY_VALUE_OF_GROUP = "value"
GROUP_ENTITY_TYPE = "entity"
GROUP_ENTITY_DICTIONARY = "entity_dict"
ENTITY_TEXT_OF_GROUP = "entity_text"
COMPLETE_MATCH_OF_GROUP = 0

# regex for: `[entity_text]((entity_type(:entity_synonym)?)|{entity_dict})`
ENTITY_REGULAR_EXPRESSION = re.compile(
    r"\[(?P<entity_text>[^\]]+?)\](\((?P<entity>[^:)]+?)(?:\:(?P<value>[^)]+))?\)|\{(?P<entity_dict>[^}]+?)\})"
)


class EntityAttri(NamedTuple):
    """Attributes of an entity defined in markdown data."""

    type: Text
    value: Text
    text: Text
    group: Optional[Text]
    role: Optional[Text]


def search_entities_in_training_example(example: Text) -> List[Dict[Text, Any]]:
    """Extracts entities from an intent example.

    Args:
        example: Intent example.

    Returns:
        Extracted entities.
    """

    entities = []
    off_set = 0

    for match in re.finditer(ENTITY_REGULAR_EXPRESSION, example):
        attributes_of_entity = extracting_entity_attributes(match)

        begin_index = match.start() - off_set
        last_index = begin_index + len(attributes_of_entity.text)
        off_set += len(match.group(0)) - len(attributes_of_entity.text)

        entity_name = convo.shared.nlu.training_data.util.building_entity(
            begin_index,
            last_index,
            attributes_of_entity.value,
            attributes_of_entity.type,
            attributes_of_entity.role,
            attributes_of_entity.group,
        )
        entities.append(entity_name)

    return entities


def extracting_entity_attributes(match: Match) -> EntityAttri:
    """Extract the entity attributes, i.e. type, value, etc., from the
    regex match.

    Args:
        match: Regex match to extract the entity attributes from.

    Returns:
        EntityAttri object.
    """
    entity_text_string = match.groupdict()[ENTITY_TEXT_OF_GROUP]

    if match.groupdict()[GROUP_ENTITY_DICTIONARY]:
        return extracting_entity_attributes_from_dictionary(entity_text_string, match)

    parser_entity_type = match.groupdict()[GROUP_ENTITY_TYPE]

    if match.groupdict()[ENTITY_VALUE_OF_GROUP]:
        parser_entity_value = match.groupdict()[ENTITY_VALUE_OF_GROUP]
    else:
        parser_entity_value = entity_text_string

    return EntityAttri(parser_entity_type, parser_entity_value, entity_text_string, None, None)


def extracting_entity_attributes_from_dictionary(
    entity_text: Text, match: Match
) -> EntityAttri:
    """Extract entity attributes from dict format.

    Args:
        entity_text: Original entity text.
        match: Regex match.

    Returns:
        Extracted entity attributes.
    """
    entity_dictionary_string = match.groupdict()[GROUP_ENTITY_DICTIONARY]
    entity_dictionary = get_valid_dictionary(entity_dictionary_string)
    return EntityAttri(
        entity_dictionary.get(ATTRIBUTE_TYPE_ENTITY),
        entity_dictionary.get(ATTRIBUTE_VALUE_ENTITY, entity_text),
        entity_text,
        entity_dictionary.get(ATTRIBUTE_GROUP_ENTITY),
        entity_dictionary.get(ATTRIBUTE_ROLE_ENTITY),
    )


def get_valid_dictionary(json_str: Text) -> Dict[Text, Text]:
    """Converts the provided `json_str` to a valid dict containing the entity
    attributes.

    Users can specify entity roles, synonyms, groups for an entity in a dict, e.g.
    [LA]{"entity": "city", "role": "to", "value": "Los Angeles"}.

    Args:
        json_str: The entity dict as string without "{}".

    Raises:
        ValidationError if validation of entity dict fails.
        JSONDecodeError if provided entity dict is not valid json.

    Returns:
        Deserialized and validated `json_str`.
    """
    import json
    import convo.shared.utils.validation as validation_utils
    import convo.shared.nlu.training_data.schemas.data_schema as schema

    # add {} as they are not part of the regex
    try:
        data = json.loads(f"{{{json_str}}}")
    except JSONDecodeError as e:
        convo.shared.utils.io.raising_warning(
            f"Incorrect training data format ('{{{json_str}}}'). Make sure your "
            f"data is valid.",
            docs=TRAINING_DATA_NLU_DOCUMENTS_URL,
        )
        raise e

    validation_utils.validating_training_data(data, schema.entity_dictionary_schema())

    return data


def replacing_entities(training_example: Text) -> Text:
    """Replace special symbols related to the entities in the provided
       training example.

    Args:
        training_example: Original training example with special symbols.

    Returns:
        String with removed special symbols.
    """
    return re.sub(
        ENTITY_REGULAR_EXPRESSION, lambda m: m.groupdict()[ENTITY_TEXT_OF_GROUP], training_example
    )


def parsing_training_example(example: Text, intent: Optional[Text] = None) -> "Msg":
    """Extract entities and synonyms, and convert to plain text."""

    entities = search_entities_in_training_example(example)
    plain_text_str = replacing_entities(example)

    return Msg.building(plain_text_str, intent, entities)
