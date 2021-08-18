import logging
import os
import typing

import numpy as np
from typing import Any, Dict, List, Optional, Text, Tuple, Type, Callable

import convo.nlu.utils.bilou_utils as bilou_utils
import convo.shared.utils.io
from convo.nlu.test import token_labels_determination
from convo.nlu.tokenizers.spacy_tokenizer import TAG_POS_KEY
from convo.nlu.config import ConvoNLUModelConfiguration
from convo.nlu.tokenizers.tokenizer import Tokenizer
from convo.nlu.components import Element
from convo.nlu.extractors.extractor import ExtractorEntity
from convo.nlu.model import Metadataset
from convo.nlu.tokenizers.tokenizer import Tkn
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
from convo.nlu.constants import NAMES_OF_TOKENS
from convo.shared.nlu.constants import (
    TXT,
    ENTITIES_NAME,
    ATTRIBUTE_TYPE_ENTITY,
    ATTRIBUTE_GROUP_ENTITY,
    ATTRIBUTE_ROLE_ENTITY,
    ENTITY_TAG_ABSENT,
)
from convo.shared.constants import COMPONENTS_DOCUMENTS_URL
from convo.utils.tensorflow.constants import FLAG_BILOU

log = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    from sklearn_crfsuite import ConditionalRandomFields


class ConditionalRandomFieldToken:
    def __init__(
        self,
        text: Text,
        pos_tag: Text,
        pattern: Dict[Text, Any],
        dense_features: np.ndarray,
        entity_tag: Text,
        entity_role_tag: Text,
        entity_group_tag: Text,
    ):
        self.text = text
        self.pos_tag = pos_tag
        self.pattern = pattern
        self.dense_features = dense_features
        self.entity_tag = entity_tag
        self.entity_role_tag = entity_role_tag
        self.entity_group_tag = entity_group_tag


class CRFEntityExtractor(ExtractorEntity):
    @classmethod
    def required_components(cls) -> List[Type[Element]]:
        return [Tokenizer]

    defaults = {
        # BILOU_flag determines whether to use BILOU tagging or not.
        # More rigorous however requires more examples per entity
        # rule of thumb: use only if more than 100 egs. per entity
        FLAG_BILOU: True,
        # crf_features is [before, token, after] array with before, token,
        # after holding keys about which features to use for each token,
        # for example, 'title' in array before will have the feature
        # "is the preceding token in title case?"
        # POS features require SpacyTokenizer
        # pattern feature require RegexFeaturizer
        "features": [
            ["low", "title", "upper"],
            [
                "low",
                "bias",
                "prefix5",
                "prefix2",
                "suffix5",
                "suffix3",
                "suffix2",
                "upper",
                "title",
                "digit",
                "pattern",
            ],
            ["low", "title", "upper"],
        ],
        # The maximum number of iterations for optimization algorithms.
        "max_iterations": 50,
        # weight of the L1 regularization
        "L1_c": 0.1,
        # weight of the L2 regularization
        "L2_c": 0.1,
        # Name of dense featurizers to use.
        # If list is empty all available dense features are used.
        "featurizers": [],
    }

    function_dict: Dict[Text, Callable[[ConditionalRandomFieldToken], Any]] = {
        "low": lambda crf_token: crf_token.text.lower(),
        "title": lambda crf_token: crf_token.text.istitle(),
        "prefix5": lambda crf_token: crf_token.text[:5],
        "prefix2": lambda crf_token: crf_token.text[:2],
        "suffix5": lambda crf_token: crf_token.text[-5:],
        "suffix3": lambda crf_token: crf_token.text[-3:],
        "suffix2": lambda crf_token: crf_token.text[-2:],
        "suffix1": lambda crf_token: crf_token.text[-1:],
        "bias": lambda crf_token: "bias",
        "pos": lambda crf_token: crf_token.pos_tag,
        "pos2": lambda crf_token: crf_token.pos_tag[:2]
        if crf_token.pos_tag is not None
        else None,
        "upper": lambda crf_token: crf_token.text.isupper(),
        "digit": lambda crf_token: crf_token.text.isdigit(),
        "pattern": lambda crf_token: crf_token.pattern,
        "text_dense_features": lambda crf_token: crf_token.dense_features,
        "entity": lambda crf_token: crf_token.entity_tag,
    }

    def __init__(
        self,
        component_config: Optional[Dict[Text, Any]] = None,
        entity_taggers: Optional[Dict[Text, "ConditionalRandomFields"]] = None,
    ) -> None:

        super().__init__(component_config)

        self.entity_taggers = entity_taggers

        self.crf_order = [
            ATTRIBUTE_TYPE_ENTITY,
            ATTRIBUTE_ROLE_ENTITY,
            ATTRIBUTE_GROUP_ENTITY,
        ]

        self._validate_config()

    def _validate_config(self) -> None:
        if len(self.component_config.get("features", [])) % 2 != 1:
            raise ValueError(
                "Need an odd number of crf feature lists to have a center word."
            )

    @classmethod
    def required_packages(cls) -> List[Text]:
        return ["sklearn_crfsuite", "sklearn"]

    def train(
        self,
        training_data: TrainingDataSet,
        config: Optional[ConvoNLUModelConfiguration] = None,
        **kwargs: Any,
    ) -> None:
        # checks whether there is at least one
        # example with an entity annotation
        if not training_data.entity_exp:
            log.debug(
                "No training examples with entities present. Skip training"
                "of 'CRFEntityExtractor'."
            )
            return

        self.check_right_entity_annotations(training_data)

        if self.component_config[FLAG_BILOU]:
            bilou_utils.bilou_apply_schema(training_data)

        # only keep the CRFs for tags we actually have training data for
        self._upgrade_crf_order(training_data)

        # filter out pre-trained entity examples
        entity_eg = self.filter_trainable_entities(training_data.nlu_exp)

        data_set = [self._transform_to_crf_tokens(example) for example in entity_eg]

        self._model_train(data_set)

    def _upgrade_crf_order(self, training_data: TrainingDataSet):
        """Train only CRFs we actually have training data for."""
        _conditional_random_field_order = []

        for tag_name in self.crf_order:
            if tag_name == ATTRIBUTE_TYPE_ENTITY and training_data.entities:
                _conditional_random_field_order.append(ATTRIBUTE_TYPE_ENTITY)
            elif tag_name == ATTRIBUTE_ROLE_ENTITY and training_data.roles_of_entity:
                _conditional_random_field_order.append(ATTRIBUTE_ROLE_ENTITY)
            elif tag_name == ATTRIBUTE_GROUP_ENTITY and training_data.groups_of_entity:
                _conditional_random_field_order.append(ATTRIBUTE_GROUP_ENTITY)

        self.crf_order = _conditional_random_field_order

    def process(self, message: Msg, **kwargs: Any) -> None:
        entities = self.fetch_entities(message)
        entities = self.add_extractor_name(entities)
        message.put(ENTITIES_NAME, message.get(ENTITIES_NAME, []) + entities, add_to_output=True)

    def fetch_entities(self, message: Msg) -> List[Dict[Text, Any]]:
        """Extract entities from the given message using the trained model(s)."""

        if self.entity_taggers is None:
            return []

        crf_entity_extractor_tokens = message.get(NAMES_OF_TOKENS[TXT])
        conditional_random_field_tokens = self._transform_to_crf_tokens(message)

        forecasts = {}
        for tag_name, entity_tagger in self.entity_taggers.items():
            # use predicted entity tags as features for second level CRFs
            add_tag_features = tag_name != ATTRIBUTE_TYPE_ENTITY
            if add_tag_features:
                self._append_tag_to_crf_token(conditional_random_field_tokens, forecasts)

            feature = self._conditional_random_field_tokens_to_features(conditional_random_field_tokens, add_tag_features)
            forecasts[tag_name] = entity_tagger.predict_marginals_single(feature)

        # convert predictions into a list of tags and a list of confidences
        labels, confidences = self._label_confidences(crf_entity_extractor_tokens, forecasts)

        return self.convert_predictions_into_entities(
            message.get(TXT), crf_entity_extractor_tokens, labels, confidences
        )

    def _append_tag_to_crf_token(
        self,
        crf_tokens: List[ConditionalRandomFieldToken],
        predictions: Dict[Text, List[Dict[Text, float]]],
    ):
        """Add predicted entity tags to ConditionalRandomFields tokens."""
        if ATTRIBUTE_TYPE_ENTITY in predictions:
            _labels, _ = self._most_likely_label(predictions[ATTRIBUTE_TYPE_ENTITY])
            for tag, token in zip(_labels, crf_tokens):
                token.entity_tag = tag

    def _most_likely_label(
        self, predictions: List[Dict[Text, float]]
    ) -> Tuple[List[Text], List[float]]:
        """Get the entity tags with the highest confidence.

        Args:
            predictions: list of mappings from entity tag to confidence value

        Returns:
            List of entity tags and list of confidence values.
        """
        _tags = []
        _confidences = []

        for token_predictions in predictions:
            label = max(token_predictions, key=lambda key: token_predictions[key])
            _tags.append(label)

            if self.component_config[FLAG_BILOU]:
                # if we are using BILOU flags, we will sum up the prob
                # of the B, I, L and U tags for an entity
                _confidences.append(
                    sum(
                        _confidence
                        for _tag, _confidence in token_predictions.items()
                        if bilou_utils.without_tag_prefix(label)
                        == bilou_utils.without_tag_prefix(_tag)
                    )
                )
            else:
                _confidences.append(token_predictions[label])

        return _tags, _confidences

    def _label_confidences(
        self, tokens: List[Tkn], predictions: Dict[Text, List[Dict[Text, float]]]
    ) -> Tuple[Dict[Text, List[Text]], Dict[Text, List[float]]]:
        """Get most likely tag predictions with confidence values for tokens."""
        tags = {}
        confidences = {}

        for tag_name, predicted_tags in predictions.items():
            if len(tokens) != len(predicted_tags):
                raise Exception(
                    "Inconsistency in amount of tokens between crfsuite and message"
                )

            _tags, _confidences = self._most_likely_label(predicted_tags)

            if self.component_config[FLAG_BILOU]:
                _tags, _confidences = bilou_utils.consistent_ensure_bilou_tagging(
                    _tags, _confidences
                )

            confidences[tag_name] = _confidences
            tags[tag_name] = _tags

        return tags, confidences

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Text = None,
        model_metadata: Metadataset = None,
        cached_component: Optional["CRFEntityExtractor"] = None,
        **kwargs: Any,
    ) -> "CRFEntityExtractor":
        import joblib

        filenames = meta.get("files")
        taggers_entity = {}

        if not filenames:
            log.debug(
                f"Failed to load model for 'CRFEntityExtractor'. "
                f"Maybe you did not provide enough training data and no model was "
                f"trained or the path '{os.path.abspath(model_dir)}' doesn't exist?"
            )
            return cls(component_config=meta)

        for name, filename in filenames.items():
            model_file = os.path.join(model_dir, filename)
            if os.path.exists(model_file):
                taggers_entity[name] = joblib.load(model_file)
            else:
                log.debug(
                    f"Failed to load model for tag '{name}' for 'CRFEntityExtractor'. "
                    f"Maybe you did not provide enough training data and no model was "
                    f"trained or the path '{os.path.abspath(model_file)}' doesn't "
                    f"exist?"
                )

        return cls(meta, taggers_entity)

    def persist(self, filename: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this model into the passed dir.

        Returns the metadata necessary to load the model again."""

        import joblib

        filenames = {}

        if self.entity_taggers:
            for name, entity_tagger in self.entity_taggers.items():
                filename = f"{filename}.{name}.pkl"
                model_filename = os.path.join(model_dir, filename)
                joblib.dump(entity_tagger, model_filename)
                filenames[name] = filename

        return {"files": filenames}

    def _conditional_random_field_tokens_to_features(
        self, crf_tokens: List[ConditionalRandomFieldToken], include_tag_features: bool = False
    ) -> List[Dict[Text, Any]]:
        """Convert the list of tokens into discrete features."""

        config_features = self.component_config["features"]
        statement_features = []

        for token_idx in range(len(crf_tokens)):
            # the features for the current token include features of the token
            # before and after the current features (if defined in the config)
            # token before (-1), current token (0), token after (+1)
            window_size_available = len(config_features)
            half_window_size_available = window_size_available // 2
            window_scope = range(-half_window_size_available, half_window_size_available + 1)

            features_token = self._generate_features_for_token(
                crf_tokens,
                token_idx,
                half_window_size_available,
                window_scope,
                include_tag_features,
            )

            statement_features.append(features_token)

        return statement_features

    def _generate_features_for_token(
        self,
        crf_tokens: List[ConditionalRandomFieldToken],
        token_idx: int,
        half_window_size: int,
        window_range: range,
        include_tag_features: bool,
    ):
        """Convert a token into discrete features including word before and word
        after."""

        config_features = self.component_config["features"]
        affixes = [str(i) for i in window_range]

        features_token = {}

        # iterate over the tokens in the window range (-1, 0, +1) to collect the
        # features for the token at token_idx
        for pointer_position in window_range:
            current_token_idx = token_idx + pointer_position

            if current_token_idx >= len(crf_tokens):
                # token is at the end of the sentence
                features_token["EOS"] = True
            elif current_token_idx < 0:
                # token is at the beginning of the sentence
                features_token["BOS"] = True
            else:
                token = crf_tokens[current_token_idx]

                # get the features to extract for the token we are currently looking at
                present_feature_idx = pointer_position + half_window_size
                feature = config_features[present_feature_idx]

                affix = affixes[present_feature_idx]

                # we add the 'entity' feature to include the entity type as features
                # for the role and group CRFs
                # (do not modify features, otherwise we will end up adding 'entity'
                # over and over again, making training very slow)
                extra_features = []
                if include_tag_features:
                    extra_features.append("entity")

                for feature in feature + extra_features:
                    if feature == "pattern":
                        # add all regexes extracted from the 'RegexFeaturizer' as a
                        # feature: 'pattern_name' is the name of the pattern the user
                        # set in the training data, 'matched' is either 'True' or
                        # 'False' depending on whether the token actually matches the
                        # pattern or not
                        regular_patterns = self.function_dict[feature](token)
                        for pattern_name, matched in regular_patterns.items():
                            features_token[
                                f"{affix}:{feature}:{pattern_name}"
                            ] = matched
                    else:
                        worth = self.function_dict[feature](token)
                        features_token[f"{affix}:{feature}"] = worth

        return features_token

    @staticmethod
    def _crf_tokens_to_labels(crf_tokens: List[ConditionalRandomFieldToken], tag_name: Text) -> List[Text]:
        """Return the list of tags for the given tag name."""
        if tag_name == ATTRIBUTE_ROLE_ENTITY:
            return [crf_token.entity_role_tag for crf_token in crf_tokens]
        if tag_name == ATTRIBUTE_GROUP_ENTITY:
            return [crf_token.entity_group_tag for crf_token in crf_tokens]

        return [crf_token.entity_tag for crf_token in crf_tokens]

    @staticmethod
    def _token_pattern(message: Msg, idx: int) -> Dict[Text, bool]:
        """Get the patterns of the token at the given index extracted by the
        'RegexFeaturizer'.

        The 'RegexFeaturizer' adds all patterns listed in the training data to the
        token. The pattern name is mapped to either 'True' (pattern applies to token) or
        'False' (pattern does not apply to token).

        Args:
            message: The message.
            idx: The token index.

        Returns:
            The pattern dict.
        """
        if message.get(NAMES_OF_TOKENS[TXT]) is not None:
            return message.get(NAMES_OF_TOKENS[TXT])[idx].get("pattern", {})
        return {}

    def _fetch_dense_features(self, message: Msg) -> Optional[List]:
        """Convert dense features to python-crfsuite feature format."""
        feature, _ = message.fetch_dense_features(
            TXT, self.component_config["featurizers"]
        )

        if feature is None:
            return None

        crf_entity_extractor_tokens = message.get(NAMES_OF_TOKENS[TXT])
        if len(crf_entity_extractor_tokens) != len(feature.features):
            convo.shared.utils.io.raising_warning(
                f"Number of dense features ({len(feature.features)}) for attribute "
                f"'TXT' does not match number of tokens ({len(crf_entity_extractor_tokens)}).",
                docs=COMPONENTS_DOCUMENTS_URL + "#crfentityextractor",
            )
            return None

        # convert to python-crfsuite feature format
        features_output = []
        for feature in feature.features:
            feature_dictionary = {
                str(index): token_features
                for index, token_features in enumerate(feature)
            }
            changed = {"text_dense_features": feature_dictionary}
            features_output.append(changed)

        return features_output

    def _transform_to_crf_tokens(self, message: Msg) -> List[ConditionalRandomFieldToken]:
        """Take a message and convert it to crfsuite format."""

        conditional_random_field_format = []
        crf_entity_extractor_tokens = message.get(NAMES_OF_TOKENS[TXT])

        text_dense_features = self._fetch_dense_features(message)
        labels = self._fetch_tags(message)

        for i, token in enumerate(crf_entity_extractor_tokens):
            pattern = self._token_pattern(message, i)
            entity = self.get_tag_for(labels, ATTRIBUTE_TYPE_ENTITY, i)
            group = self.get_tag_for(labels, ATTRIBUTE_GROUP_ENTITY, i)
            role = self.get_tag_for(labels, ATTRIBUTE_ROLE_ENTITY, i)
            pos_tag = token.get(TAG_POS_KEY)
            dense_features = (
                text_dense_features[i] if text_dense_features is not None else []
            )

            conditional_random_field_format.append(
                ConditionalRandomFieldToken(
                    text=token.text,
                    pos_tag=pos_tag,
                    entity_tag=entity,
                    entity_group_tag=group,
                    entity_role_tag=role,
                    pattern=pattern,
                    dense_features=dense_features,
                )
            )

        return conditional_random_field_format

    def _fetch_tags(self, message: Msg) -> Dict[Text, List[Text]]:
        """Get assigned entity tags of message."""
        crf_entity_extractor_tokens = message.get(NAMES_OF_TOKENS[TXT])
        tags = {}

        for tag_name in self.crf_order:
            if self.component_config[FLAG_BILOU]:
                bilou_keyname = bilou_utils.bilou_get_key_for_tags(tag_name)
                if message.get(bilou_keyname):
                    _tags = message.get(bilou_keyname)
                else:
                    _tags = [ENTITY_TAG_ABSENT for _ in crf_entity_extractor_tokens]
            else:
                _tags = [
                    token_labels_determination(
                        token, message.get(ENTITIES_NAME), attribute_key=tag_name
                    )
                    for token in crf_entity_extractor_tokens
                ]
            tags[tag_name] = _tags

        return tags

    def _model_train(self, df_train: List[List[ConditionalRandomFieldToken]]) -> None:
        """Train the crf tagger based on the training data."""
        import sklearn_crfsuite

        self.entity_taggers = {}

        for tag_name in self.crf_order:
            log.debug(f"Training ConditionalRandomFields for '{tag_name}'.")

            # add entity tag features for second level CRFs
            add_tag_features = tag_name != ATTRIBUTE_TYPE_ENTITY
            train_X = [
                self._conditional_random_field_tokens_to_features(sentence, add_tag_features)
                for sentence in df_train
            ]
            train_y = [
                self._crf_tokens_to_labels(sentence, tag_name) for sentence in df_train
            ]

            tagger_entity = sklearn_crfsuite.CRF(
                algorithm="lbfgs",
                # coefficient for L1 penalty
                c1=self.component_config["L1_c"],
                # coefficient for L2 penalty
                c2=self.component_config["L2_c"],
                # stop earlier
                max_iterations=self.component_config["max_iterations"],
                # include transitions that are possible, but not observed
                all_possible_transitions=True,
            )
            tagger_entity.fit(train_X, train_y)

            self.entity_taggers[tag_name] = tagger_entity

            log.debug("Training finished.")
