from typing import Any, Text, List, Dict

from convo.shared.nlu.constants import (
    ATTRIBUTE_VALUE_ENTITY,
    ATTRIBUTE_START_ENTITY,
    ATTRIBUTE_END_ENTITY,
)


def adding_synonyms_from_entities(
    plain_text: Text, entities: List[Dict], existing_synonyms: Dict[Text, Any]
) -> None:
    """Adds synonyms found in intent examples.

    Args:
        plain_text: Plain (with removed special symbols) user utterance.
        entities: Entities that were extracted from the original user utterance.
        existing_synonyms: The dict with existing synonyms mappings that will
                           be extended.
    """
    for e in entities:
        exp_text = plain_text[e[ATTRIBUTE_START_ENTITY] : e[ATTRIBUTE_END_ENTITY]]
        if exp_text != e[ATTRIBUTE_VALUE_ENTITY]:
            adding_synonyms(exp_text, e[ATTRIBUTE_VALUE_ENTITY], existing_synonyms)


def adding_synonyms(
    synonym_value: Text, synonym_name: Text, existing_synonyms: Dict[Text, Any]
) -> None:
    """Adds a new synonym mapping to the provided list of synonyms.

    Args:
        synonym_value: Value of the synonym.
        synonym_name: Name of the synonym.
        existing_synonyms: Dictionary will synonym mappings that will be extended.
    """
    import convo.shared.nlu.training_data.util as training_data_util

    training_data_util.duplicate_synonym_check(
        existing_synonyms, synonym_value, synonym_name, "reading markdown"
    )
    existing_synonyms[synonym_value] = synonym_name
