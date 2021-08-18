import logging
from collections import defaultdict, Counter
from typing import List, Tuple, Text, Optional, Dict, Any

from convo.nlu.tokenizers.tokenizer import Tkn
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
from convo.nlu.constants import (
    NAMES_OF_TOKENS,
    ENTITIES_BILOU,
    ENTITIES_GROUP_BILOU,
    ENTITIES_ROLE_BILOU,
)
from convo.shared.nlu.constants import (
    TXT,
    ENTITIES_NAME,
    ATTRIBUTE_START_ENTITY,
    ATTRIBUTE_END_ENTITY,
    ATTRIBUTE_TYPE_ENTITY,
    ATTRIBUTE_GROUP_ENTITY,
    ATTRIBUTE_ROLE_ENTITY,
    ENTITY_TAG_ABSENT,
)

log = logging.getLogger(__name__)

BEGIN = "B-"
IN_SIDE = "I-"
END = "L-"
SECTION = "U-"
PREFIXES_BILOU = [BEGIN, IN_SIDE, END, SECTION]


def prefix_bilou_from_tag(tag: Text) -> Optional[Text]:
    """Returns the BILOU prefix from the given tag.

    Args:
        tag: the tag

    Returns: the BILOU prefix of the tag
    """
    if tag[:2] in PREFIXES_BILOU:
        return tag[:2]
    return None


def without_tag_prefix(tag: Text) -> Text:
    """Remove the BILOU prefix from the given tag.

    Args:
        tag: the tag

    Returns: the tag without the BILOU prefix
    """
    if tag[:2] in PREFIXES_BILOU:
        return tag[2:]
    return tag


def tags_bilou_to_id(
    message: Msg,
    tag_id_dict: Dict[Text, int],
    tag_name: Text = ATTRIBUTE_TYPE_ENTITY,
) -> List[int]:
    """Maps the entity tags of the message to the ids of the provided dict.

    Args:
        message: the message
        tag_id_dict: mapping of tags to ids
        tag_name: tag name of interest

    Returns: a list of tag ids
    """
    key_bilou = bilou_get_key_for_tags(tag_name)

    if message.get(key_bilou):
        _label = [
            tag_id_dict[_tag] if _tag in tag_id_dict else tag_id_dict[ENTITY_TAG_ABSENT]
            for _tag in message.get(key_bilou)
        ]
    else:
        _label = [tag_id_dict[ENTITY_TAG_ABSENT] for _ in message.get(NAMES_OF_TOKENS[TXT])]

    return _label


def bilou_get_key_for_tags(tag_name: Text) -> Text:
    """Get the message key for the BILOU tagging format of the provided tag name.

    Args:
        tag_name: the tag name

    Returns:
        the message key to store the BILOU tags
    """
    if tag_name == ATTRIBUTE_ROLE_ENTITY:
        return ENTITIES_ROLE_BILOU

    if tag_name == ATTRIBUTE_GROUP_ENTITY:
        return ENTITIES_GROUP_BILOU

    return ENTITIES_BILOU


def bilou_removes_prefixes(tags: List[Text]) -> List[Text]:
    """Removes the BILOU prefixes from the given list of tags.

    Args:
        tags: the list of tags

    Returns:
        list of tags without BILOU prefix
    """
    return [without_tag_prefix(t) for t in tags]


def build_tag_id_dictionary(
    training_data: TrainingDataSet, tag_name: Text = ATTRIBUTE_TYPE_ENTITY
) -> Optional[Dict[Text, int]]:
    """Create a mapping of unique tags to ids.

    Args:
        training_data: the training data
        tag_name: tag name of interest

    Returns: a mapping of tags to ids
    """
    key_bilou = bilou_get_key_for_tags(tag_name)

    labels_distinct = set(
        [
            without_tag_prefix(e)
            for example in training_data.nlu_exp
            if example.get(key_bilou)
            for e in example.get(key_bilou)
        ]
    ) - {ENTITY_TAG_ABSENT}

    if not labels_distinct:
        return None

    dict_tag_id = {
        f"{prefix}{tag}": idx_1 * len(PREFIXES_BILOU) + idx_2 + 1
        for idx_1, tag in enumerate(sorted(labels_distinct))
        for idx_2, prefix in enumerate(PREFIXES_BILOU)
    }
    # ENTITY_TAG_ABSENT corresponds to non-entity which should correspond to 0 index
    # needed for correct prediction for padding
    dict_tag_id[ENTITY_TAG_ABSENT] = 0

    return dict_tag_id


def bilou_apply_schema(training_data: TrainingDataSet) -> None:
    """Get a list of BILOU entity tags and set them on the given messages.

    Args:
        training_data: the training data
    """
    for message in training_data.nlu_exp:
        entity = message.get(ENTITIES_NAME)

        if not entity:
            continue

        tkns = message.get(NAMES_OF_TOKENS[TXT])

        for attribute, message_key in [
            (ATTRIBUTE_TYPE_ENTITY, ENTITIES_BILOU),
            (ATTRIBUTE_ROLE_ENTITY, ENTITIES_ROLE_BILOU),
            (ATTRIBUTE_GROUP_ENTITY, ENTITIES_GROUP_BILOU),
        ]:
            entity = message_map_entities(message, attribute)
            output = tags_bilou_from_offsets(tkns, entity)
            message.put(message_key, output)


def message_map_entities(
    message: Msg, attribute_key: Text = ATTRIBUTE_TYPE_ENTITY
) -> List[Tuple[int, int, Text]]:
    """Maps the entities of the given message to their start, end, and tag values.

    Args:
        message: the message
        attribute_key: key of tag value to use

    Returns: a list of start, end, and tag value tuples
    """

    def convert_entity(entity: Dict[Text, Any]) -> Tuple[int, int, Text]:
        return (
            entity[ATTRIBUTE_START_ENTITY],
            entity[ATTRIBUTE_END_ENTITY],
            entity.get(attribute_key) or ENTITY_TAG_ABSENT,
        )

    entity = [convert_entity(entity) for entity in message.get(ENTITIES_NAME, [])]

    # entities is a list of tuples (start, end, tag value).
    # filter out all entities with tag value == ENTITY_TAG_ABSENT.
    index_tag_value = 2
    return [entity for entity in entity if entity[index_tag_value] != ENTITY_TAG_ABSENT]


def tags_bilou_from_offsets(
    tokens: List[Tkn], entities: List[Tuple[int, int, Text]]
) -> List[Text]:
    """Creates BILOU tags for the given tokens and entities.

    Args:
        message: The message object.
        tokens: The list of tokens.
        entities: The list of start, end, and tag tuples.
        missing: The tag for missing entities.

    Returns:
        BILOU tags.
    """
    start_pos_to_tkn_id = {token.start: i for i, token in enumerate(tokens)}
    last_pos_to_tkn_id = {token.end: i for i, token in enumerate(tokens)}

    bilou = [ENTITY_TAG_ABSENT for _ in tokens]

    tags_add_bilou_to_entities(
        bilou, entities, last_pos_to_tkn_id, start_pos_to_tkn_id
    )

    return bilou


def tags_add_bilou_to_entities(
    bilou: List[Text],
    entities: List[Tuple[int, int, Text]],
    end_pos_to_token_idx: Dict[int, int],
    start_pos_to_token_idx: Dict[int, int],
):
    for start_pos, end_pos, label in entities:
        start_token_idx = start_pos_to_token_idx.get(start_pos)
        end_token_idx = end_pos_to_token_idx.get(end_pos)

        # Only interested if the tokenization is correct
        if start_token_idx is not None and end_token_idx is not None:
            if start_token_idx == end_token_idx:
                bilou[start_token_idx] = f"{SECTION}{label}"
            else:
                bilou[start_token_idx] = f"{BEGIN}{label}"
                for i in range(start_token_idx + 1, end_token_idx):
                    bilou[i] = f"{IN_SIDE}{label}"
                bilou[end_token_idx] = f"{END}{label}"


def consistent_ensure_bilou_tagging(
    predicted_tags: List[Text], predict_confidence: List[float]
) -> Tuple[List[Text], List[float]]:
    """
    Ensure predicted tags follow the BILOU tagging schema.

    We assume that starting B- tags are correct. Followed tags that belong to start
    label but have a different entity type are updated considering also the confidence
    values of those tags.
    For example, B-a I-b L-a is updated to B-a I-a L-a and B-a I-a O is changed to
    B-a L-a.

    Args:
        predicted_tags: predicted tags
        predict_confidence: predicted confidences

    Return:
        List of tags.
        List of confidences.
    """

    for idx, predicted_tag in enumerate(predicted_tags):
        affix = prefix_bilou_from_tag(predicted_tag)
        label = without_tag_prefix(predicted_tag)

        if affix == BEGIN:
            last_index = _search_bilou_end(idx, predicted_tags)

            relevant_confidence = predict_confidence[idx: last_index + 1]
            relevant_labels = [
                without_tag_prefix(tag) for tag in predicted_tags[idx: last_index + 1]
            ]

            # if not all tags are the same, for example, B-person I-person L-location
            # we need to check what label we should use depending on the confidence
            # values and update the tags and confidences accordingly
            if not all(relevant_labels[0] == tag for tag in relevant_labels):
                # decide which label this entity should use
                label, tag_score = _use_to_tag(relevant_labels, relevant_confidence)

                log.debug(
                    f"Using label '{label}' for entity with mixed label labels "
                    f"(original tags: {predicted_tags[idx : last_index + 1]}, "
                    f"(original confidences: "
                    f"{predict_confidence[idx: last_index + 1]})."
                )

                # all tags that change get the score of that label assigned
                predict_confidence = _update_confidences(
                    predict_confidence, predicted_tags, label, tag_score, idx, last_index
                )

            # ensure correct BILOU annotations
            if last_index == idx:
                predicted_tags[idx] = f"{SECTION}{label}"
            elif last_index - idx == 1:
                predicted_tags[idx] = f"{BEGIN}{label}"
                predicted_tags[last_index] = f"{END}{label}"
            else:
                predicted_tags[idx] = f"{BEGIN}{label}"
                predicted_tags[last_index] = f"{END}{label}"
                for i in range(idx + 1, last_index):
                    predicted_tags[i] = f"{IN_SIDE}{label}"

    return predicted_tags, predict_confidence


def _use_to_tag(
    relevant_tags: List[Text], relevant_confidences: List[float]
) -> Tuple[Text, float]:
    """Decide what tag to use according to the following metric:

    Calculate the average confidence per tag.
    Calculate the percentage of tokens assigned to a tag within the entity per tag.
    The harmonic mean of those two metrics is the score for the tag.
    The tag with the highest score is taken as the tag for the entity.

    Args:
        relevant_tags: The tags of the entity.
        relevant_confidences: The confidence values.

    Returns:
        The tag to use. The score of that tag.
    """
    # Calculate the average confidence per tag.
    average_confidence_per_label = _average_confidence_per_tag(
        relevant_tags, relevant_confidences
    )
    # Calculate the percentage of tokens assigned to a tag per tag.
    tkn_percentage_per_tag = Counter(relevant_tags)
    for label, count in tkn_percentage_per_tag.items():
        tkn_percentage_per_tag[label] = round(count / len(relevant_tags), 2)

    # Calculate the harmonic mean between the two metrics per tag.
    per_tag_score = {}
    for label, token_percentage in tkn_percentage_per_tag.items():
        average_confidence = average_confidence_per_label[label]
        per_tag_score[label] = (
            2
            * (average_confidence * token_percentage)
            / (average_confidence + token_percentage)
        )

    # Take the tag with the highest score as the tag for the entity
    label = max(per_tag_score, key=per_tag_score.get)
    result = per_tag_score[label]

    return label, result


def _update_confidences(
    predicted_confidences: List[float],
    predicted_tags: List[Text],
    tag: Text,
    score: float,
    idx: int,
    last_idx: int,
):
    """Update the confidence values.

    Set the confidence value of a tag to score value if the predicated
    tag changed.

    Args:
        predicted_confidences: The list of predicted confidences.
        predicted_tags: The list of predicted tags.
        tag: The tag of the entity.
        score: The score value of that tag.
        idx: The start index of the entity.
        last_idx: The end index of the entity.

    Returns:
        The updated list of confidences.
    """
    for i in range(idx, last_idx + 1):
        predicted_confidences[i] = (
            round(score, 2)
            if without_tag_prefix(predicted_tags[i]) != tag
            else predicted_confidences[i]
        )
    return predicted_confidences


def _average_confidence_per_tag(
    relevant_tags: List[Text], relevant_confidences: List[float]
) -> Dict[Text, float]:
    tag_per_confidence = defaultdict(list)

    for tag, confidence in zip(relevant_tags, relevant_confidences):
        tag_per_confidence[tag].append(confidence)

    average_confidence_per_tag = {}
    for tag, confidences in tag_per_confidence.items():
        average_confidence_per_tag[tag] = round(sum(confidences) / len(confidences), 2)

    return average_confidence_per_tag


def _search_bilou_end(start_idx: int, predicted_tags: List[Text]) -> int:
    """Find the last index of the entity.

    The start index is pointing to a B- label. The entity is closed as soon as we find
    a L- label or a O label.

    Args:
        start_idx: The start index of the entity
        predicted_tags: The list of predicted tags

    Returns:
        The end index of the entity
    """
    current_index = start_idx + 1
    ended = False
    begin_tag = without_tag_prefix(predicted_tags[start_idx])

    while not ended:
        if current_index >= len(predicted_tags):
            log.debug(
                "Inconsistent BILOU tagging found, B- label not closed by L- label, "
                "i.e [B-a, I-a, O] instead of [B-a, L-a, O].\n"
                "Assuming last label is L- instead of I-."
            )
            current_index -= 1
            break

        current_tag = predicted_tags[current_index]
        affix = prefix_bilou_from_tag(current_tag)
        label = without_tag_prefix(current_tag)

        if label != begin_tag:
            # words are not tagged the same entity class
            log.debug(
                "Inconsistent BILOU tagging found, B- label, L- label pair encloses "
                "multiple entity classes.i.e. [B-a, I-b, L-a] instead of "
                "[B-a, I-a, L-a].\nAssuming B- class is correct."
            )

        if affix == END:
            ended = True
        elif affix == IN_SIDE:
            # middle part of the entity
            current_index += 1
        else:
            # entity not closed by an L- label
            ended = True
            current_index -= 1
            log.debug(
                "Inconsistent BILOU tagging found, B- label not closed by L- label, "
                "i.e [B-a, I-a, O] instead of [B-a, L-a, O].\n"
                "Assuming last label is L- instead of I-."
            )

    return current_index
