from typing import Any, Optional, Tuple, Text, Dict, Set, List

import typing
import copy

import convo.shared.utils.io
from convo.shared.exceptions import ConvoExceptions 
from convo.shared.nlu.constants import (
    TXT,
    INTENTION,
    RETURN_RESPONSE,
    KEY_INTENT_RESPONSE,
    META_DATA,
    META_DATA_INTENT,
    META_DATA_EXAMPLE,
    ENTITIES_NAME,
    RESP_IDENTIFIER_DELIMITER,
    FEATURED_TYPE_SENTENCE,
    FEATURED_TYPE_SEQUENCE,
    ACT_TEXT,
    ACT_NAME,
)

if typing.TYPE_CHECKING:
    from convo.shared.nlu.training_data.features import Features


class Msg:
    def __init__(
        self,
        data: Optional[Dict[Text, Any]] = None,
        output_properties: Optional[Set] = None,
        time: Optional[Text] = None,
        features: Optional[List["Features"]] = None,
        **kwargs: Any,
    ) -> None:
        self.time = time
        self.data = data.copy() if data else {}
        self.features = features if features else []

        self.data.update(**kwargs)

        if output_properties:
            self.output_properties = output_properties
        else:
            self.output_properties = set()
        self.output_properties.add(TXT)

    def adding_features(self, features: Optional["Features"]) -> None:
        if features is not None:
            self.features.append(features)

    def put(self, prop, info, add_to_output=False) -> None:
        self.data[prop] = info
        if add_to_output:
            self.output_properties.add(prop)

    def get(self, prop, default=None) -> Any:
        return self.data.get(prop, default)

    def as_dictionary_nlu(self) -> dict:
        """Get dict representation of message as it would appear in training data"""

        e = self.as_dictionary()
        if e.get(INTENTION, None):
            e[INTENTION] = self.get_complete_intent()
        e.pop(RETURN_RESPONSE, None)
        e.pop(KEY_INTENT_RESPONSE, None)
        return e

    def as_dictionary(self, only_output_properties=False) -> dict:
        if only_output_properties:
            e = {
                key: value
                for key, value in self.data.items()
                if key in self.output_properties
            }
        else:
            e = self.data

        # Filter all keys with None value. These could have come while building the
        # Msg object in markdown format
        return {key: value for key, value in e.items() if value is not None}

    def __eq__(self, others) -> bool:
        if not isinstance(others, Msg):
            return False
        else:
            return ordering(others.data) == ordering(self.data)

    def __hash__(self) -> int:
        return hash(str(ordering(self.data)))

    @classmethod
    def building(
        cls,
        text: Text,
        intent: Optional[Text] = None,
        entities: Optional[List[Dict[Text, Any]]] = None,
        intent_metadata: Optional[Any] = None,
        example_metadata: Optional[Any] = None,
        **kwargs: Any,
    ) -> "Msg":
        """
        Build a Msg from `UserUttered` data.
        Args:
            text: text of a user's utterance
            intent: an intent of the user utterance
            entities: entities in the user's utterance
            intent_metadata: optional metadata for the intent
            example_metadata: optional metadata for the intent example
        Returns:
            Msg
        """
        data: Dict[Text, Any] = {TXT: text}
        if intent:
            split_intent, response_key = cls.split_intent_response_key(intent)
            if split_intent:
                data[INTENTION] = split_intent
            if response_key:
                # intent label can be of the form - {intent}/{response_key},
                # so store the full intent label in intent_response_key
                data[KEY_INTENT_RESPONSE] = intent
        if entities:
            data[ENTITIES_NAME] = entities
        if intent_metadata is not None:
            data[META_DATA] = {META_DATA_INTENT: intent_metadata}
        if example_metadata is not None:
            # pytype: disable=unsupported-operands
            data.setdefault(META_DATA, {})[META_DATA_EXAMPLE] = example_metadata
            # pytype: enable=unsupported-operands
        return cls(data, **kwargs)

    def get_complete_intent(self) -> Text:
        """Get intent as it appears in training data"""

        return (
            self.get(KEY_INTENT_RESPONSE)
            if self.get(KEY_INTENT_RESPONSE)
            else self.get(INTENTION)
        )

    def fetch_combined_intent_response_key(self) -> Text:
        """Get intent as it appears in training data"""

        convo.shared.utils.io.raising_warning(
            "`fetch_combined_intent_response_key` is deprecated and "
            "will be removed in future versions. "
            "Please use `get_full_intent` instead.",
            category=DeprecationWarning,
        )
        return self.get_complete_intent()

    @staticmethod
    def split_intent_response_key(
        original_intent: Text,
    ) -> Tuple[Text, Optional[Text]]:

        split_title = original_intent.split(RESP_IDENTIFIER_DELIMITER)
        if len(split_title) == 2:
            return split_title[0], split_title[1]
        elif len(split_title) == 1:
            return split_title[0], None

        raise ConvoExceptions (
            f"Intent name '{original_intent}' is invalid, "
            f"it cannot contain more than one '{RESP_IDENTIFIER_DELIMITER}'."
        )

    def fetch_sparse_features(
        self, attribute: Text, featurizers: Optional[List[Text]] = None
    ) -> Tuple[Optional["Features"], Optional["Features"]]:
        """Get all sparse features for the given attribute that are coming from the
        given list of featurizers.
        If no featurizers are provided, all available features will be considered.
        Args:
            attribute: message attribute
            featurizers: names of featurizers to consider
        Returns:
            Sparse features.
        """
        if featurizers is None:
            featurizers = []

        sequential_features, statement_features = self.sparse_features__filter(
            attribute, featurizers
        )

        sequential_features = self.combining_features(sequential_features, featurizers)
        statement_features = self.combining_features(statement_features, featurizers)

        return sequential_features, statement_features

    def fetch_dense_features(
        self, attribute: Text, featurizers: Optional[List[Text]] = None
    ) -> Tuple[Optional["Features"], Optional["Features"]]:
        """Get all dense features for the given attribute that are coming from the given
        list of featurizers.
        If no featurizers are provided, all available features will be considered.
        Args:
            attribute: message attribute
            featurizers: names of featurizers to consider
        Returns:
            Dense features.
        """
        if featurizers is None:
            featurizers = []

        sequential_features, statement_features = self.dense_features_filter(
            attribute, featurizers
        )

        sequential_features = self.combining_features(sequential_features, featurizers)
        statement_features = self.combining_features(statement_features, featurizers)

        return sequential_features, statement_features

    def features_available(
        self, attribute: Text, featurizers: Optional[List[Text]] = None
    ) -> bool:
        """Check if there are any features present for the given attribute and
        featurizers.
        If no featurizers are provided, all available features will be considered.
        Args:
            attribute: message attribute
            featurizers: names of featurizers to consider
        Returns:
            ``True``, if features are present, ``False`` otherwise
        """
        if featurizers is None:
            featurizers = []

        (
            sequence_sparse_features,
            sentence_sparse_features,
        ) = self.sparse_features__filter(attribute, featurizers)
        sequence_dense_features, sentence_dense_features = self.dense_features_filter(
            attribute, featurizers
        )

        return (
            len(sequence_sparse_features) > 0
            or len(sentence_sparse_features) > 0
            or len(sequence_dense_features) > 0
            or len(sentence_dense_features) > 0
        )

    def dense_features_filter(
        self, attribute: Text, featurizers: List[Text]
    ) -> Tuple[List["Features"], List["Features"]]:
        statement_features = [
            f
            for f in self.features
            if f.attribute == attribute
            and f.dense_check()
            and f.type == FEATURED_TYPE_SENTENCE
            and (f.origin in featurizers or not featurizers)
        ]
        sequential_features = [
            f
            for f in self.features
            if f.attribute == attribute
            and f.dense_check()
            and f.type == FEATURED_TYPE_SEQUENCE
            and (f.origin in featurizers or not featurizers)
        ]
        return sequential_features, statement_features

    def sparse_features__filter(
        self, attribute: Text, featurizers: List[Text]
    ) -> Tuple[List["Features"], List["Features"]]:
        statement_features = [
            f
            for f in self.features
            if f.attribute == attribute
            and f.sparse_check()
            and f.type == FEATURED_TYPE_SENTENCE
            and (f.origin in featurizers or not featurizers)
        ]
        sequential_features = [
            f
            for f in self.features
            if f.attribute == attribute
            and f.sparse_check()
            and f.type == FEATURED_TYPE_SEQUENCE
            and (f.origin in featurizers or not featurizers)
        ]

        return sequential_features, statement_features

    @staticmethod
    def combining_features(
        features: List["Features"], featurizers: Optional[List[Text]] = None
    ) -> Optional["Features"]:
        already_combined_features = None

        for f in features:
            if already_combined_features is None:
                already_combined_features = copy.deepcopy(f)
                already_combined_features.origin = featurizers
            else:
                already_combined_features.combine_features(f)

        return already_combined_features

    def is_core_msg(self) -> bool:
        """Checks whether the message is a core message or not.

        E.g. a core message is created from a story, not from the NLU data.

        Returns:
            True, if message is a core message, false otherwise.
        """
        return bool(
            self.data.get(ACT_NAME)
            or self.data.get(ACT_TEXT)
            or (
                (self.data.get(INTENTION) or self.data.get(RETURN_RESPONSE))
                and not self.data.get(TXT)
            )
            or (
                self.data.get(TXT)
                and not (self.data.get(INTENTION) or self.data.get(RETURN_RESPONSE))
            )
        )


def ordering(obj: Any) -> Any:
    if isinstance(obj, dict):
        return sorted((k, ordering(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordering(x) for x in obj)
    else:
        return obj
