from typing import Any, Dict, List, Text, Tuple, Optional

import convo.shared.utils.io
from convo.shared.constants import TRAINING_DATA_NLU_DOCUMENTS_URL
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
from convo.nlu.tokenizers.tokenizer import Tkn
from convo.nlu.components import Element
from convo.nlu.constants import (
    NAMES_OF_TOKENS,
    ENTITY_ATTR_CONFIDENCE_TYPE_VAL,
    ENTITY_ATTR_CONFIDENCE_ROLE,
    ENTITY_ATTR_CONFIDENCE_GRP,
)
from convo.shared.nlu.constants import (
    TXT,
    INTENTION,
    ENTITIES_NAME,
    ATTRIBUTE_VALUE_ENTITY,
    ATTRIBUTE_START_ENTITY,
    ATTRIBUTE_END_ENTITY,
    EXTRACTOR,
    ATTRIBUTE_TYPE_ENTITY,
    ATTRIBUTE_GROUP_ENTITY,
    ATTRIBUTE_ROLE_ENTITY,
    ENTITY_TAG_ABSENT,
)


class ExtractorEntity(Element):
    def add_extractor_name(
        self, entities: List[Dict[Text, Any]]
    ) -> List[Dict[Text, Any]]:
        for entity in entities:
            entity[EXTRACTOR] = self.name
        return entities

    def add_processor_name(self, entity: Dict[Text, Any]) -> Dict[Text, Any]:
        if "processors" in entity:
            entity["processors"].append(self.name)
        else:
            entity["processors"] = [self.name]

        return entity

    @staticmethod
    def filter_irrelevant_entities(extracted: list, requested_dimensions: set) -> list:
        """Only return dimensions the user configured"""

        if requested_dimensions:
            return [
                entity
                for entity in extracted
                if entity[ATTRIBUTE_TYPE_ENTITY] in requested_dimensions
            ]
        return extracted

    @staticmethod
    def find_entity(
        entity: Dict[Text, Any], text: Text, tokens: List[Tkn]
    ) -> Tuple[int, int]:
        off_sets = [token.start for token in tokens]
        over = [token.end for token in tokens]

        if entity[ATTRIBUTE_START_ENTITY] not in off_sets:
            msg = (
                "Invalid entity {} in example '{}': "
                "entities must span whole tokens. "
                "Wrong entity start.".format(entity, text)
            )
            raise ValueError(msg)

        if entity[ATTRIBUTE_END_ENTITY] not in over:
            msg = (
                "Invalid entity {} in example '{}': "
                "entities must span whole tokens. "
                "Wrong entity end.".format(entity, text)
            )
            raise ValueError(msg)

        begin = off_sets.index(entity[ATTRIBUTE_START_ENTITY])
        over = over.index(entity[ATTRIBUTE_END_ENTITY]) + 1
        return begin, over

    def filter_trainable_entities(
        self, entity_examples: List[Msg]
    ) -> List[Msg]:
        """Filters out untrainable entity annotations.

        Creates a copy of entity_examples in which entities that have
        `extractor` set to something others than
        self.name (e.g. 'CRFEntityExtractor') are removed.
        """

        filtered_data = []
        for message in entity_examples:
            entities = []
            for ent in message.get(ENTITIES_NAME, []):
                get_extractor = ent.get(EXTRACTOR)
                if not get_extractor or get_extractor == self.name:
                    entities.append(ent)
            data_set = message.data.copy()
            data_set[ENTITIES_NAME] = entities
            filtered_data.append(
                Msg(
                    text=message.get(TXT),
                    data=data_set,
                    output_properties=message.output_properties,
                    time=message.time,
                    features=message.features,
                )
            )

        return filtered_data

    def convert_predictions_into_entities(
        self,
        text: Text,
        tokens: List[Tkn],
        tags: Dict[Text, List[Text]],
        confidences: Optional[Dict[Text, List[float]]] = None,
    ) -> List[Dict[Text, Any]]:
        """
        Convert predictions into entities.

        Args:
            text: The text message.
            tokens: Msg tokens without CLS token.
            tags: Predicted tags.
            confidences: Confidences of predicted tags.

        Returns:
            Entities.
        """
        import convo.nlu.utils.bilou_utils as bilou_utils

        entities = []

        final_entity_tag = ENTITY_TAG_ABSENT
        final_role_tag = ENTITY_TAG_ABSENT
        final_group_tag = ENTITY_TAG_ABSENT
        final_token_end = -1

        for idx, token in enumerate(tokens):
            present_entity_tag = self.get_tag_for(tags, ATTRIBUTE_TYPE_ENTITY, idx)

            if present_entity_tag == ENTITY_TAG_ABSENT:
                final_entity_tag = ENTITY_TAG_ABSENT
                final_token_end = token.end
                continue

            present_group_tag = self.get_tag_for(tags, ATTRIBUTE_GROUP_ENTITY, idx)
            present_group_tag = bilou_utils.without_tag_prefix(present_group_tag)
            present_role_tag = self.get_tag_for(tags, ATTRIBUTE_ROLE_ENTITY, idx)
            present_role_tag = bilou_utils.without_tag_prefix(present_role_tag)

            convert_group_or_role = (
                final_group_tag != present_group_tag or final_role_tag != present_role_tag
            )

            if bilou_utils.prefix_bilou_from_tag(present_entity_tag):
                # checks for new bilou tag
                # new bilou tag begins are not with I- , L- tags
                new_bilou_tag_begins = final_entity_tag != present_entity_tag and (
                    bilou_utils.END
                    != bilou_utils.prefix_bilou_from_tag(present_entity_tag)
                    and bilou_utils.IN_SIDE
                    != bilou_utils.prefix_bilou_from_tag(present_entity_tag)
                )

                # to handle bilou tags such as only I-, L- tags without B-tag
                # and handle multiple U-tags consecutively
                new_unigram_bilou_tag_begins = (
                    final_entity_tag == ENTITY_TAG_ABSENT
                    or bilou_utils.SECTION
                    == bilou_utils.prefix_bilou_from_tag(present_entity_tag)
                )

                new_tag_got = (
                    new_bilou_tag_begins
                    or new_unigram_bilou_tag_begins
                    or convert_group_or_role
                )
                final_entity_tag = present_entity_tag
                present_entity_tag = bilou_utils.without_tag_prefix(present_entity_tag)
            else:
                new_tag_got = (
                    final_entity_tag != present_entity_tag or convert_group_or_role
                )
                final_entity_tag = present_entity_tag

            if new_tag_got:
                # new entity found
                entity = self._generate_new_entity(
                    list(tags.keys()),
                    present_entity_tag,
                    present_group_tag,
                    present_role_tag,
                    token,
                    idx,
                    confidences,
                )
                entities.append(entity)
            elif token.start - final_token_end <= 1:
                # current token has the same entity tag as the token before and
                # the two tokens are only separated by at most one symbol (e.g. space,
                # dash, etc.)
                entities[-1][ATTRIBUTE_END_ENTITY] = token.end
                if confidences is not None:
                    self._upgrade_confidence_values(entities, confidences, idx)
            else:
                # the token has the same entity tag as the token before but the two
                # tokens are separated by at least 2 symbols (e.g. multiple spaces,
                # a comma and a space, etc.)
                entity = self._generate_new_entity(
                    list(tags.keys()),
                    present_entity_tag,
                    present_group_tag,
                    present_role_tag,
                    token,
                    idx,
                    confidences,
                )
                entities.append(entity)

            final_group_tag = present_group_tag
            final_role_tag = present_role_tag
            final_token_end = token.end

        for entity in entities:
            entity[ATTRIBUTE_VALUE_ENTITY] = text[
                entity[ATTRIBUTE_START_ENTITY] : entity[ATTRIBUTE_END_ENTITY]
            ]

        return entities

    @staticmethod
    def _upgrade_confidence_values(
        entities: List[Dict[Text, Any]], confidences: Dict[Text, List[float]], idx: int
    ):
        # use the lower confidence value
        entities[-1][ENTITY_ATTR_CONFIDENCE_TYPE_VAL] = min(
            entities[-1][ENTITY_ATTR_CONFIDENCE_TYPE_VAL],
            confidences[ATTRIBUTE_TYPE_ENTITY][idx],
        )
        if ATTRIBUTE_ROLE_ENTITY in entities[-1]:
            entities[-1][ENTITY_ATTR_CONFIDENCE_ROLE] = min(
                entities[-1][ENTITY_ATTR_CONFIDENCE_ROLE],
                confidences[ATTRIBUTE_ROLE_ENTITY][idx],
            )
        if ATTRIBUTE_GROUP_ENTITY in entities[-1]:
            entities[-1][ENTITY_ATTR_CONFIDENCE_GRP] = min(
                entities[-1][ENTITY_ATTR_CONFIDENCE_GRP],
                confidences[ATTRIBUTE_GROUP_ENTITY][idx],
            )

    @staticmethod
    def get_tag_for(tags: Dict[Text, List[Text]], tag_name: Text, idx: int) -> Text:
        """Get the value of the given tag name from the list of tags.

        Args:
            tags: Mapping of tag name to list of tags;
            tag_name: The tag name of interest.
            idx: The index position of the tag.

        Returns:
            The tag value.
        """
        if tag_name in tags:
            return tags[tag_name][idx]
        return ENTITY_TAG_ABSENT

    @staticmethod
    def _generate_new_entity(
        tag_names: List[Text],
        entity_tag: Text,
        group_tag: Text,
        role_tag: Text,
        token: Tkn,
        idx: int,
        confidences: Optional[Dict[Text, List[float]]] = None,
    ) -> Dict[Text, Any]:
        """Create a new entity.

        Args:
            tag_names: The tag names to include in the entity.
            entity_tag: The entity type value.
            group_tag: The entity group value.
            role_tag: The entity role value.
            token: The token.
            confidence: The confidence value.

        Returns:
            Created entity.
        """
        entity = {
            ATTRIBUTE_TYPE_ENTITY: entity_tag,
            ATTRIBUTE_START_ENTITY: token.start,
            ATTRIBUTE_END_ENTITY: token.end,
        }

        if confidences is not None:
            entity[ENTITY_ATTR_CONFIDENCE_TYPE_VAL] = confidences[
                ATTRIBUTE_TYPE_ENTITY
            ][idx]

        if ATTRIBUTE_ROLE_ENTITY in tag_names and role_tag != ENTITY_TAG_ABSENT:
            entity[ATTRIBUTE_ROLE_ENTITY] = role_tag
            if confidences is not None:
                entity[ENTITY_ATTR_CONFIDENCE_ROLE] = confidences[
                    ATTRIBUTE_ROLE_ENTITY
                ][idx]
        if ATTRIBUTE_GROUP_ENTITY in tag_names and group_tag != ENTITY_TAG_ABSENT:
            entity[ATTRIBUTE_GROUP_ENTITY] = group_tag
            if confidences is not None:
                entity[ENTITY_ATTR_CONFIDENCE_GRP] = confidences[
                    ATTRIBUTE_GROUP_ENTITY
                ][idx]

        return entity

    @staticmethod
    def check_right_entity_annotations(training_data: TrainingDataSet) -> None:
        """Check if entities are correctly annotated in the training data.

        If the start and end values of an entity do not match any start and end values
        of the respected token, we define an entity as misaligned and log a warning.

        Args:
            training_data: The training data.
        """
        for example in training_data.entity_exp:
            boundaries_entity = [
                (entity[ATTRIBUTE_START_ENTITY], entity[ATTRIBUTE_END_ENTITY])
                for entity in example.get(ENTITIES_NAME)
            ]
            token_beginning_positions = [t.start for t in example.get(NAMES_OF_TOKENS[TXT])]
            token_last_positions = [t.end for t in example.get(NAMES_OF_TOKENS[TXT])]

            for entity_start, entity_end in boundaries_entity:
                if (
                    entity_start not in token_beginning_positions
                    or entity_end not in token_last_positions
                ):
                    convo.shared.utils.io.raising_warning(
                        f"Misaligned entity annotation in message '{example.get(TXT)}' "
                        f"with intent '{example.get(INTENTION)}'. Make sure the start and "
                        f"end values of entities in the training data match the token "
                        f"boundaries (e.g. entities don't include trailing whitespaces "
                        f"or punctuation).",
                        docs=TRAINING_DATA_NLU_DOCUMENTS_URL,
                    )
                    break
