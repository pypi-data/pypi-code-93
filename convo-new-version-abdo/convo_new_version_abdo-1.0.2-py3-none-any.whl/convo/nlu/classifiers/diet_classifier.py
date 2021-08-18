import copy
import logging
from collections import defaultdict
from pathlib import Path

import numpy as np
import os
import scipy.sparse
import tensorflow as tf
import tensorflow_addons as tfa

from typing import Any, Dict, List, Optional, Text, Tuple, Union, Type, NamedTuple

import convo.shared.utils.io
import convo.utils.io as io_utils
import convo.nlu.utils.bilou_utils as bilou_utils
from convo.nlu.featurizers.featurizer import Featurizer
from convo.nlu.components import Element
from convo.nlu.classifiers.classifier import IntentionClassifier
from convo.nlu.extractors.extractor import ExtractorEntity
from convo.nlu.test import token_labels_determination
from convo.nlu.classifiers import LABEL_RANKING_LENGTH
from convo.utils import train_utils
from convo.utils.tensorflow import layers
from convo.utils.tensorflow.models import ConvoModel, ConverterConvoModel
from convo.utils.tensorflow.model_data import ConvoModelDataSet, FeatureSign
from convo.nlu.constants import NAMES_OF_TOKENS
from convo.shared.nlu.constants import (
    TXT,
    INTENTION,
    KEY_INTENT_RESPONSE,
    ENTITIES_NAME,
    ATTRIBUTE_TYPE_ENTITY,
    ATTRIBUTE_GROUP_ENTITY,
    ATTRIBUTE_ROLE_ENTITY,
    ENTITY_TAG_ABSENT,
)
from convo.nlu.config import ConvoNLUModelConfiguration, InvalidConfigurationError
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
from convo.nlu.model import Metadataset
from convo.utils.tensorflow.constants import (
    STAGE,
    SIZES_OF_HIDDEN_LAYERS,
    SHARED_HIDDEN_LAYERS,
    TRANSFORMER_DIMENSION,
    NUMBER_TRANSFORMER_LAYERS,
    NUMBER_HEADS,
    BATCH_SIZE,
    GROUP_STRATEGY,
    EPOCHS,
    RAND_SEED,
    RATE_OF_LEARNING,
    LENGTH_RANKING,
    LOSS_CATEGORY,
    SIMILARITY_TYPE_CATEGORY,
    NUMBER_NEG,
    SPARSE_INP_DROP_OUT,
    DENSE_INP_DROP_OUT,
    COVERED_LM,
    ENTITY_IDENTIFICATION,
    TENSOR_BOARD_LOG_DIRECTORY,
    INTENT_CLASSIFY,
    EVALUATE_NUM_EXAMPLES,
    EVALUATE_NUMBER_EPOCHS,
    UNI_DIRECTIONAL_ENCODER,
    DROP_PRICE,
    ATTENTION_DROP_RATE,
    WEIGHT_SPARSE,
    NEG_MARGIN_SCALE,
    REGULARIZATION_CONST,
    LOSS_SCALE,
    USE_MAXIMUM_NEGATIVE_SIMILARITY,
    MAXIMUM_NEGATIVE_SIMILARITY,
    MAXIMUM_POSITIVE_SIMILARITY,
    EMBEDDING_CAPACITY,
    FLAG_BILOU,
    RELATIVE_ATTENTION_KEY,
    RELATIVE_ATTENTION_VAL,
    RELATIVE_POSITION_MAXIMUM,
    SOFT_MAX,
    AUTOMATIC,
    BALANCED_VALUE,
    TENSOR_BOARD_LOGGING_LEVEL,
    CONCATENATE_DIMENSION,
    FEATURES,
    CHECK_POINT_MODEL,
    SEQUENTIAL,
    SENTENCE,
    DIMENSION_DENSE,
)


log = logging.getLogger(__name__)


INFREQUENT = "sparse"
CONCENTRATED = "dense"
SEQUENCE_LEN = f"{SEQUENTIAL}_lengths"
TAG_KEY = STAGE
TAG_SUB_KEY = "ids"
TAG_ID = "tag_ids"

POSSIBLE_TAG = [ATTRIBUTE_TYPE_ENTITY, ATTRIBUTE_ROLE_ENTITY, ATTRIBUTE_GROUP_ENTITY]


class EntityTagSpecification(NamedTuple):
    """Specification of an entity tag present in the training data."""

    tag_name: Text
    ids_to_tags: Dict[int, Text]
    tags_to_ids: Dict[Text, int]
    num_tags: int


class DIETClassifier(IntentionClassifier, ExtractorEntity):
    """DIET (Dual Intent and Entity Transformer) is a multi-task architecture for
    intent classification and entity recognition.

    The architecture is based on a transformer which is shared for both tasks.
    A sequence of entity labels is predicted through a Conditional Random Field (ConditionalRandomFields)
    tagging layer on top of the transformer output sequence corresponding to the
    input sequence of tokens. The transformer output for the ``__CLS__`` token and
    intent labels are embedded into a single semantic vector space. We use the
    dot-product loss to maximize the similarity with the target label and minimize
    similarities with negative samples.
    """

    @classmethod
    def required_components(cls) -> List[Type[Element]]:
        return [Featurizer]

    # please make sure to update the docs when changing a default parameter
    defaults = {
        # ## Architecture of the used neural network
        # Hidden layer sizes for layers before the embedding layers for user message
        # and labels.
        # The number of hidden layers is equal to the length of the corresponding
        # list.
        SIZES_OF_HIDDEN_LAYERS: {TXT: [], STAGE: []},
        # Whether to share the hidden layer weights between user message and labels.
        SHARED_HIDDEN_LAYERS: False,
        # Number of units in transformer
        TRANSFORMER_DIMENSION: 256,
        # Number of transformer layers
        NUMBER_TRANSFORMER_LAYERS: 2,
        # Number of attention heads in transformer
        NUMBER_HEADS: 4,
        # If 'True' use key relative embeddings in attention
        RELATIVE_ATTENTION_KEY: False,
        # If 'True' use value relative embeddings in attention
        RELATIVE_ATTENTION_VAL: False,
        # Max position for relative embeddings
        RELATIVE_POSITION_MAXIMUM: None,
        # Use a unidirectional or bidirectional encoder.
        UNI_DIRECTIONAL_ENCODER: False,
        # ## Training parameters
        # Initial and final batch sizes:
        # Batch size will be linearly increased for each epoch.
        BATCH_SIZE: [64, 256],
        # Strategy used when creating batches.
        # Can be either 'sequence' or 'balanced'.
        GROUP_STRATEGY: BALANCED_VALUE,
        # Number of epochs to train
        EPOCHS: 300,
        # Set random seed to any 'int' to get reproducible results
        RAND_SEED: None,
        # Initial learning rate for the optimizer
        RATE_OF_LEARNING: 0.001,
        # ## Parameters for embeddings
        # Dimension size of embedding vectors
        EMBEDDING_CAPACITY: 20,
        # Default dense dimension to use if no dense features are present.
        DIMENSION_DENSE: {TXT: 128, STAGE: 20},
        # Default dimension to use for concatenating sequence and sentence features.
        CONCATENATE_DIMENSION: {TXT: 128, STAGE: 20},
        # The number of incorrect labels. The algorithm will minimize
        # their similarity to the user input during training.
        NUMBER_NEG: 20,
        # Type of similarity measure to use, either 'auto' or 'cosine' or 'inner'.
        SIMILARITY_TYPE_CATEGORY: AUTOMATIC,
        # The type of the loss function, either 'softmax' or 'margin'.
        LOSS_CATEGORY: SOFT_MAX,
        # Number of top actions to normalize scores for loss type 'softmax'.
        # Set to 0 to turn off normalization.
        LENGTH_RANKING: 10,
        # Indicates how similar the algorithm should try to make embedding vectors
        # for correct labels.
        # Should be 0.0 < ... < 1.0 for 'cosine' similarity type.
        MAXIMUM_POSITIVE_SIMILARITY: 0.8,
        # Maximum negative similarity for incorrect labels.
        # Should be -1.0 < ... < 1.0 for 'cosine' similarity type.
        MAXIMUM_NEGATIVE_SIMILARITY: -0.4,
        # If 'True' the algorithm only minimizes maximum similarity over
        # incorrect intent labels, used only if 'loss_type' is set to 'margin'.
        USE_MAXIMUM_NEGATIVE_SIMILARITY: True,
        # If 'True' scale loss inverse proportionally to the confidence
        # of the correct prediction
        LOSS_SCALE: False,
        # ## Regularization parameters
        # The scale of regularization
        REGULARIZATION_CONST: 0.002,
        # The scale of how important is to minimize the maximum similarity
        # between embeddings of different labels,
        # used only if 'loss_type' is set to 'margin'.
        NEG_MARGIN_SCALE: 0.8,
        # Dropout rate for encoder
        DROP_PRICE: 0.2,
        # Dropout rate for attention
        ATTENTION_DROP_RATE: 0,
        # Sparsity of the weights in dense layers
        WEIGHT_SPARSE: 0.8,
        # If 'True' apply dropout to sparse input tensors
        SPARSE_INP_DROP_OUT: True,
        # If 'True' apply dropout to dense input tensors
        DENSE_INP_DROP_OUT: True,
        # ## Evaluation parameters
        # How often calculate validation accuracy.
        # Small values may hurt performance, e.g. model accuracy.
        EVALUATE_NUMBER_EPOCHS: 20,
        # How many examples to use for hold out validation set
        # Large values may hurt performance, e.g. model accuracy.
        EVALUATE_NUM_EXAMPLES: 0,
        # ## Model config
        # If 'True' intent classification is trained and intent predicted.
        INTENT_CLASSIFY: True,
        # If 'True' named entity recognition is trained and entities predicted.
        ENTITY_IDENTIFICATION: True,
        # If 'True' random tokens of the input message will be masked and the model
        # should predict those tokens.
        COVERED_LM: False,
        # 'BILOU_flag' determines whether to use BILOU tagging or not.
        # If set to 'True' labelling is more rigorous, however more
        # examples per entity are required.
        # Rule of thumb: you should have more than 100 examples per entity.
        FLAG_BILOU: True,
        # If you want to use tensorboard to visualize training and validation metrics,
        # set this option to a valid output dir.
        TENSOR_BOARD_LOG_DIRECTORY: None,
        # Define when training metrics for tensorboard should be logged.
        # Either after every epoch or for every training step.
        # Valid values: 'epoch' and 'minibatch'
        TENSOR_BOARD_LOGGING_LEVEL: "epoch",
        # Perform model checkpointing
        CHECK_POINT_MODEL: False,
        # Specify what features to use as sequence and sentence features
        # By default all features in the pipeline are used.
        FEATURES: [],
    }

    # init helpers
    def _examine_masked_lm(self) -> None:
        if (
            self.component_config[COVERED_LM]
            and self.component_config[NUMBER_TRANSFORMER_LAYERS] == 0
        ):
            raise ValueError(
                f"If number of transformer layers is 0, "
                f"'{COVERED_LM}' option should be 'False'."
            )

    def _examine_share_hidden_layers_sizes(self) -> None:
        if self.component_config.get(SHARED_HIDDEN_LAYERS):
            first_hidden_layer_sizes = next(
                iter(self.component_config[SIZES_OF_HIDDEN_LAYERS].vals())
            )
            # check that all hidden layer sizes are the same
            similar_hidden_layer_sizes = all(
                current_hidden_layer_sizes == first_hidden_layer_sizes
                for current_hidden_layer_sizes in self.component_config[
                    SIZES_OF_HIDDEN_LAYERS
                ].vals()
            )
            if not similar_hidden_layer_sizes:
                raise ValueError(
                    f"If hidden layer weights are shared, "
                    f"{SIZES_OF_HIDDEN_LAYERS} must coincide."
                )

    def _check_config_params(self) -> None:
        self.component_config = train_utils.validating_deprecated_options(
            self.component_config
        )

        self._examine_masked_lm()
        self._examine_share_hidden_layers_sizes()

        self.component_config = train_utils.updating_similarity_type(
            self.component_config
        )
        self.component_config = train_utils.updating_evaluation_params(
            self.component_config
        )

    # package safety checks
    @classmethod
    def required_packages(cls) -> List[Text]:
        return ["tensorflow"]

    def __init__(
        self,
        component_config: Optional[Dict[Text, Any]] = None,
        index_label_id_mapping: Optional[Dict[int, Text]] = None,
        entity_tag_specs: Optional[List[EntityTagSpecification]] = None,
        model: Optional[ConvoModel] = None,
    ) -> None:
        """Declare instance variables with default values."""

        if component_config is not None and EPOCHS not in component_config:
            convo.shared.utils.io.raising_warning(
                f"Please configure the number of '{EPOCHS}' in your configuration file."
                f" We will change the default value of '{EPOCHS}' in the future to 1. "
            )

        super().__init__(component_config)
        self._check_config_params()

        # transform numbers to labels
        self.index_label_id_mapping = index_label_id_mapping

        self._entity_tag_specs = entity_tag_specs

        self.model = model

        self._label_data: Optional[ConvoModelDataSet] = None
        self._data_example: Optional[Dict[Text, List[np.ndarray]]] = None

    @property
    def tag_key(self) -> Optional[Text]:
        return TAG_KEY if self.component_config[INTENT_CLASSIFY] else None

    @property
    def tag_sub_key(self) -> Optional[Text]:
        return TAG_SUB_KEY if self.component_config[INTENT_CLASSIFY] else None

    @staticmethod
    def model_class() -> Type[ConvoModel]:
        return DIET

    # training data helpers:
    @staticmethod
    def _label_id_indices_mapping(
        training_data: TrainingDataSet, attribute: Text
    ) -> Dict[Text, int]:
        """Create label_id dictionary."""

        different_label_ids = {
            example.get(attribute) for example in training_data.intent_exp
        } - {None}
        return {
            label_id: idx for idx, label_id in enumerate(sorted(different_label_ids))
        }

    @staticmethod
    def _invert_mapping(mapping: Dict) -> Dict:
        return {value: key for key, value in mapping.items()}

    def _generate_entity_tag_specs(
        self, training_data: TrainingDataSet
    ) -> List[EntityTagSpecification]:
        """Create entity tag specifications with their respective tag id mappings."""

        _tag_specification = []

        for tag_name in POSSIBLE_TAG:
            if self.component_config[FLAG_BILOU]:
                tag_id_index_mapping = bilou_utils.build_tag_id_dictionary(
                    training_data, tag_name
                )
            else:
                tag_id_index_mapping = self._tag_id_indices_mapping_for(
                    tag_name, training_data
                )

            if tag_id_index_mapping:
                _tag_specification.append(
                    EntityTagSpecification(
                        tag_name=tag_name,
                        tags_to_ids=tag_id_index_mapping,
                        ids_to_tags=self._invert_mapping(tag_id_index_mapping),
                        num_tags=len(tag_id_index_mapping),
                    )
                )

        return _tag_specification

    @staticmethod
    def _tag_id_indices_mapping_for(
        tag_name: Text, training_data: TrainingDataSet
    ) -> Optional[Dict[Text, int]]:
        """Create mapping from tag name to id."""
        if tag_name == ATTRIBUTE_ROLE_ENTITY:
            different_tags = training_data.roles_of_entity
        elif tag_name == ATTRIBUTE_GROUP_ENTITY:
            different_tags = training_data.groups_of_entity
        else:
            different_tags = training_data.entities

        different_tags = different_tags - {ENTITY_TAG_ABSENT} - {None}

        if not different_tags:
            return None

        tag_id_dictionary = {
            tag_id: idx for idx, tag_id in enumerate(sorted(different_tags), 1)
        }
        # ENTITY_TAG_ABSENT corresponds to non-entity which should correspond to 0 index
        # needed for correct prediction for padding
        tag_id_dictionary[ENTITY_TAG_ABSENT] = 0

        return tag_id_dictionary

    @staticmethod
    def _search_example_for_tag(
        label: Text, examples: List[Msg], attribute: Text
    ) -> Optional[Msg]:
        for ex in examples:
            if ex.get(attribute) == label:
                return ex
        return None

    def _examine_tags_features_exist(
        self, labels_example: List[Msg], attribute: Text
    ) -> bool:
        """Checks if all labels have features set."""

        return all(
            label_example.features_available(
                attribute, self.component_config[FEATURES]
            )
            for label_example in labels_example
        )

    def _withdraw_features(
        self, message: Msg, attribute: Text
    ) -> Dict[Text, Union[scipy.sparse.spmatrix, np.ndarray]]:
        (
            sparse_sequence_features,
            sparse_sentence_features,
        ) = message.fetch_sparse_features(attribute, self.component_config[FEATURES])
        dense_sequence_features, dense_sentence_features = message.fetch_dense_features(
            attribute, self.component_config[FEATURES]
        )

        if dense_sequence_features is not None and sparse_sequence_features is not None:
            if (
                dense_sequence_features.features.shape[0]
                != sparse_sequence_features.features.shape[0]
            ):
                raise ValueError(
                    f"Sequence dimensions for sparse and dense sequence features "
                    f"don't coincide in '{message.get(TXT)}' for attribute '{attribute}'."
                )
        if dense_sentence_features is not None and sparse_sentence_features is not None:
            if (
                dense_sentence_features.features.shape[0]
                != sparse_sentence_features.features.shape[0]
            ):
                raise ValueError(
                    f"Sequence dimensions for sparse and dense sentence features "
                    f"don't coincide in '{message.get(TXT)}' for attribute '{attribute}'."
                )

        # If we don't use the transformer and we don't want to do entity recognition,
        # to speed up training take only the sentence features as feature vector.
        # We would not make use of the sequence anyway in this setup. Carrying over
        # those features to the actual training process takes quite some time.
        if (
            self.component_config[NUMBER_TRANSFORMER_LAYERS] == 0
            and not self.component_config[ENTITY_IDENTIFICATION]
            and attribute not in [INTENTION, KEY_INTENT_RESPONSE]
        ):
            sparse_sequence_features = None
            dense_sequence_features = None

        output = {}

        if sparse_sentence_features is not None:
            output[f"{INFREQUENT}_{SENTENCE}"] = sparse_sentence_features.features
        if sparse_sequence_features is not None:
            output[f"{INFREQUENT}_{SEQUENTIAL}"] = sparse_sequence_features.features
        if dense_sentence_features is not None:
            output[f"{CONCENTRATED}_{SENTENCE}"] = dense_sentence_features.features
        if dense_sequence_features is not None:
            output[f"{CONCENTRATED}_{SEQUENTIAL}"] = dense_sequence_features.features

        return output

    def _check_input_dimension_consistency(self, model_data: ConvoModelDataSet) -> None:
        """Checks if features have same dimensionality if hidden layers are shared."""

        if self.component_config.get(SHARED_HIDDEN_LAYERS):
            num_text_sentence_features = model_data.ftr_dimension(TXT, SENTENCE)
            num_label_sentence_features = model_data.ftr_dimension(STAGE, SENTENCE)
            num_text_sequence_features = model_data.ftr_dimension(TXT, SEQUENTIAL)
            num_label_sequence_features = model_data.ftr_dimension(STAGE, SEQUENTIAL)

            if (0 < num_text_sentence_features != num_label_sentence_features > 0) or (
                0 < num_text_sequence_features != num_label_sequence_features > 0
            ):
                raise ValueError(
                    "If embeddings are shared text features and label features "
                    "must coincide. Check the output dimensions of previous components."
                )

    def _withdraw_tags_precomputed_features(
        self, label_examples: List[Msg], attribute: Text = INTENTION
    ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """Collects precomputed encodings."""

        attributes = defaultdict(list)

        for e in label_examples:
            tag_features = self._withdraw_features(e, attribute)
            for feature_key, feature_value in tag_features.items():
                attributes[feature_key].append(feature_value)

        seq_features = []
        statement_features = []
        for feature_name, feature_value in attributes.items():
            if SEQUENTIAL in feature_name:
                seq_features.append(np.array(attributes[feature_name]))
            else:
                statement_features.append(np.array(attributes[feature_name]))

        return (seq_features, statement_features)

    @staticmethod
    def _compute_by_default_tag_features(
        labels_example: List[Msg],
    ) -> List[np.ndarray]:
        """Computes one-hot representation for the labels."""

        log.debug("No label features found. Computing default label features.")

        matrix_eye = np.eye(len(labels_example), dtype=np.float32)
        # add sequence dimension to one-hot labels
        return [np.array([np.expand_dims(a, 0) for a in matrix_eye])]

    def _create_label_data(
        self,
        training_data: TrainingDataSet,
        label_id_dict: Dict[Text, int],
        attribute: Text,
    ) -> ConvoModelDataSet:
        """Create matrix with label_ids encoded in rows as bag of words.

        Find a training example for each label and get the encoded features
        from the corresponding Msg object.
        If the features are already computed, fetch them from the message object
        else compute a one hot encoding for the label as the feature vector.
        """

        # Collect one example for each label
        labels_idx_eg = []
        for label_name, idx in label_id_dict.items():
            label_example = self._search_example_for_tag(
                label_name, training_data.intent_exp, attribute
            )
            labels_idx_eg.append((idx, label_example))

        # Sort the list of tuples based on label_idx
        labels_idx_eg = sorted(labels_idx_eg, key=lambda x: x[0])
        labels_eg = [example for (_, example) in labels_idx_eg]

        # Collect features, precomputed if they exist, else compute on the fly
        if self._examine_tags_features_exist(labels_eg, attribute):
            (
                sequence_features,
                sentence_features,
            ) = self._withdraw_tags_precomputed_features(labels_eg, attribute)
        else:
            sequence_features = None
            sentence_features = self._compute_by_default_tag_features(labels_eg)

        label_data_set = ConvoModelDataSet()
        label_data_set.adding_features(STAGE, SEQUENTIAL, sequence_features)
        label_data_set.adding_features(STAGE, SENTENCE, sentence_features)

        if label_data_set.feature_exist_check(
            STAGE, SENTENCE
        ) and label_data_set.feature_exist_check(STAGE, SEQUENTIAL):
            raise ValueError(
                "No label features are present. Please check your configuration file."
            )

        label_id = np.array([idx for (idx, _) in labels_idx_eg])
        # explicitly add last dimension to label_ids
        # to track correctly dynamic sequences
        label_data_set.adding_features(
            TAG_KEY, TAG_SUB_KEY, [np.expand_dims(label_id, -1)]
        )

        label_data_set.adding_len(STAGE, SEQUENCE_LEN, STAGE, SEQUENTIAL)

        return label_data_set

    def _use_by_default_tag_features(self, label_ids: np.ndarray) -> List[np.ndarray]:
        all_tag_features = self._label_data.get(STAGE, SENTENCE)[0]
        return [np.array([all_tag_features[label_id] for label_id in label_ids])]

    def _create_model_data(
        self,
        training_data: List[Msg],
        label_id_dict: Optional[Dict[Text, int]] = None,
        label_attribute: Optional[Text] = None,
        training: bool = True,
    ) -> ConvoModelDataSet:
        """Prepare data for training and create a ConvoModelDataSet object"""

        # TODO: simplify model data creation
        #   convert training data into a list of attribute to features and reuse some
        #   of the methods of TED (they most likely need to change a bit)

        attributes = defaultdict(lambda: defaultdict(list))
        tag_ids = []

        for example in training_data:
            if label_attribute is None or example.get(label_attribute):
                text_features = self._withdraw_features(example, TXT)
                for feature_key, feature_value in text_features.items():
                    attributes[TXT][feature_key].append(feature_value)

            # only add features for intent labels during training
            if training and example.get(label_attribute):
                label_features = self._withdraw_features(example, label_attribute)
                for feature_key, feature_value in label_features.items():
                    attributes[STAGE][feature_key].append(feature_value)

                if label_id_dict:
                    tag_ids.append(label_id_dict[example.get(label_attribute)])

            # only add tag_ids during training
            if training and self.component_config.get(ENTITY_IDENTIFICATION):
                for tag_spec in self._entity_tag_specs:
                    attributes[ENTITIES_NAME][tag_spec.tag_name].append(
                        self._mark_ids_for_crf(example, tag_spec)
                    )

        fetch_model_data = ConvoModelDataSet(
            label_key=self.tag_key, label_sub_key=self.tag_sub_key
        )
        for key, attribute_features in attributes.items():
            for sub_key, _features in attribute_features.items():
                sub_key = sub_key.replace(f"{INFREQUENT}_", "").replace(f"{CONCENTRATED}_", "")
                fetch_model_data.adding_features(key, sub_key, [np.array(_features)])

        if (
            label_attribute
            and fetch_model_data.feature_exist_check(STAGE, SENTENCE)
            and fetch_model_data.feature_exist_check(STAGE, SEQUENTIAL)
        ):
            # no label features are present, get default features from _label_data
            fetch_model_data.adding_features(
                STAGE, SENTENCE, self._use_by_default_tag_features(np.array(tag_ids))
            )

        # explicitly add last dimension to label_ids
        # to track correctly dynamic sequences
        fetch_model_data.adding_features(
            TAG_KEY, TAG_SUB_KEY, [np.expand_dims(tag_ids, -1)]
        )

        fetch_model_data.adding_len(TXT, SEQUENCE_LEN, TXT, SEQUENTIAL)
        fetch_model_data.adding_len(STAGE, SEQUENCE_LEN, STAGE, SEQUENTIAL)

        return fetch_model_data

    def _mark_ids_for_crf(self, example: Msg, tag_spec: EntityTagSpecification) -> np.ndarray:
        """Create a np.array containing the tag ids of the given message."""
        if self.component_config[FLAG_BILOU]:
            _labels = bilou_utils.tags_bilou_to_id(
                example, tag_spec.tags_to_ids, tag_spec.tag_name
            )
        else:
            _labels = []
            for token in example.get(NAMES_OF_TOKENS[TXT]):
                _tag = token_labels_determination(
                    token, example.get(ENTITIES_NAME), attribute_key=tag_spec.tag_name
                )
                _labels.append(tag_spec.tags_to_ids[_tag])

        # transpose to have seq_len x 1
        return np.array([_labels]).T

    # train helpers
    def preprocess_train_data(self, training_data: TrainingDataSet) -> ConvoModelDataSet:
        """Prepares data for training.

        Performs sanity checks on training data, extracts encodings for labels.
        """

        if self.component_config[FLAG_BILOU]:
            bilou_utils.bilou_apply_schema(training_data)

        label_id_index_mapping = self._label_id_indices_mapping(
            training_data, attribute=INTENTION
        )

        if not label_id_index_mapping:
            # no labels are present to train
            return ConvoModelDataSet()

        self.index_label_id_mapping = self._invert_mapping(label_id_index_mapping)

        self._label_data = self._create_label_data(
            training_data, label_id_index_mapping, attribute=INTENTION
        )

        self._entity_tag_specs = self._generate_entity_tag_specs(training_data)

        label_attr = (
            INTENTION if self.component_config[INTENT_CLASSIFY] else None
        )

        fetch_model_data = self._create_model_data(
            training_data.nlu_exp,
            label_id_index_mapping,
            label_attribute=label_attr,
        )

        self._check_input_dimension_consistency(fetch_model_data)

        return fetch_model_data

    @staticmethod
    def _examine_enough_tags(model_data: ConvoModelDataSet) -> bool:
        return len(np.unique(model_data.get(TAG_KEY, TAG_SUB_KEY))) >= 2

    def train(
        self,
        training_data: TrainingDataSet,
        config: Optional[ConvoNLUModelConfiguration] = None,
        **kwargs: Any,
    ) -> None:
        """Train the embedding intent classifier on a data set."""
        fetch_model_data = self.preprocess_train_data(training_data)
        if fetch_model_data.empty_check():
            log.debug(
                f"Cannot train '{self.__class__.__name__}'. No data was provided. "
                f"Skipping training of the classifier."
            )
            return

        if self.component_config.get(INTENT_CLASSIFY):
            if not self._examine_enough_tags(fetch_model_data):
                log.error(
                    f"Cannot train '{self.__class__.__name__}'. "
                    f"Need at least 2 different intent classes. "
                    f"Skipping training of classifier."
                )
                return
        if self.component_config.get(ENTITY_IDENTIFICATION):
            self.check_right_entity_annotations(training_data)

        # keep one example for persisting and loading
        self._data_example = fetch_model_data.first_data_exp()

        self.model = self._instant_model_class(fetch_model_data)

        self.model.fit(
            fetch_model_data,
            self.component_config[EPOCHS],
            self.component_config[BATCH_SIZE],
            self.component_config[EVALUATE_NUM_EXAMPLES],
            self.component_config[EVALUATE_NUMBER_EPOCHS],
            self.component_config[GROUP_STRATEGY],
        )

    # process helpers
    def _forecast(self, message: Msg) -> Optional[Dict[Text, tf.Tensor]]:
        if self.model is None:
            log.debug(
                f"There is no trained model for '{self.__class__.__name__}': The "
                f"component is either not trained or didn't receive enough training "
                f"data."
            )
            return None

        # create session data from message and convert it into a batch of 1
        fetch_model_data = self._create_model_data([message], training=False)

        return self.model.predict(fetch_model_data)

    def _forecast_tag(
        self, predict_out: Optional[Dict[Text, tf.Tensor]]
    ) -> Tuple[Dict[Text, Any], List[Dict[Text, Any]]]:
        """Predicts the intent of the provided message."""

        tags = {"name": None, "id": None, "confidence": 0.0}
        tag_ranking = []

        if predict_out is None:
            return tags, tag_ranking

        msg_sim = predict_out["i_scores"].numpy()

        msg_sim = msg_sim.flatten()  # sim is a matrix

        tag_id = msg_sim.argsort()[::-1]

        if (
            self.component_config[LOSS_CATEGORY] == SOFT_MAX
            and self.component_config[LENGTH_RANKING] > 0
        ):
            msg_sim = train_utils.normalization(
                msg_sim, self.component_config[LENGTH_RANKING]
            )

        msg_sim[::-1].sort()
        msg_sim = msg_sim.tolist()

        # if X contains all zeros do not predict some label
        if tag_id.size > 0:
            tags = {
                "id": hash(self.index_label_id_mapping[tag_id[0]]),
                "name": self.index_label_id_mapping[tag_id[0]],
                "confidence": msg_sim[0],
            }

            if (
                self.component_config[LENGTH_RANKING]
                and 0 < self.component_config[LENGTH_RANKING] < LABEL_RANKING_LENGTH
            ):
                output_length = self.component_config[LENGTH_RANKING]
            else:
                output_length = LABEL_RANKING_LENGTH

            rank = list(zip(list(tag_id), msg_sim))
            rank = rank[:output_length]
            tag_ranking = [
                {
                    "id": hash(self.index_label_id_mapping[label_idx]),
                    "name": self.index_label_id_mapping[label_idx],
                    "confidence": score,
                }
                for label_idx, score in rank
            ]

        return tags, tag_ranking

    def _forecast_entities(
        self, predict_out: Optional[Dict[Text, tf.Tensor]], message: Msg
    ) -> List[Dict]:
        if predict_out is None:
            return []

        forecasted_tags, confidence_evaluates = self._label_to_tags_entity(predict_out)

        entities = self.convert_predictions_into_entities(
            message.get(TXT),
            message.get(NAMES_OF_TOKENS[TXT], []),
            forecasted_tags,
            confidence_evaluates,
        )

        entities = self.add_extractor_name(entities)
        entities = message.get(ENTITIES_NAME, []) + entities

        return entities

    def _label_to_tags_entity(
        self, predict_out: Dict[Text, Any]
    ) -> Tuple[Dict[Text, List[Text]], Dict[Text, List[float]]]:
        forecasted_tags = {}
        confidence_evaluates = {}

        for tag_spec in self._entity_tag_specs:
            forecasts = predict_out[f"e_{tag_spec.tag_name}_ids"].numpy()
            fetch_confidence = predict_out[f"e_{tag_spec.tag_name}_scores"].numpy()
            fetch_confidence = [float(c) for c in fetch_confidence[0]]
            labels = [tag_spec.ids_to_tags[p] for p in forecasts[0]]

            if self.component_config[FLAG_BILOU]:
                labels, fetch_confidence = bilou_utils.consistent_ensure_bilou_tagging(
                    labels, fetch_confidence
                )

            forecasted_tags[tag_spec.tag_name] = labels
            confidence_evaluates[tag_spec.tag_name] = fetch_confidence

        return forecasted_tags, confidence_evaluates

    def process(self, message: Msg, **kwargs: Any) -> None:
        """Return the most likely label and its similarity to the input."""

        output = self._forecast(message)

        if self.component_config[INTENT_CLASSIFY]:
            label, label_ranking = self._forecast_tag(output)

            message.put(INTENTION, label, add_to_output=True)
            message.put("intent_ranking", label_ranking, add_to_output=True)

        if self.component_config[ENTITY_IDENTIFICATION]:
            entities = self._forecast_entities(output, message)

            message.put(ENTITIES_NAME, entities, add_to_output=True)

    def persist(self, filename: Text, model_directory: Text) -> Dict[Text, Any]:
        """Persist this model into the passed dir.

        Return the metadata necessary to load the model again.
        """

        if self.model is None:
            return {"file": None}

        model_directory = Path(model_directory)
        fetch_tf_model_file = model_directory / f"{filename}.tf_model"

        convo.shared.utils.io.create_dir_from_file(fetch_tf_model_file)

        if self.model.checkpoint_model:
            self.model.copying_best(str(fetch_tf_model_file))
        else:
            self.model.save(str(fetch_tf_model_file))

        io_utils.pick_data(
            model_directory / f"{filename}.data_example.pkl", self._data_example
        )
        io_utils.pick_data(
            model_directory / f"{filename}.label_data.pkl", dict(self._label_data.data)
        )
        io_utils.dictionary_pickle(
            model_directory / f"{filename}.index_label_id_mapping.json",
            self.index_label_id_mapping,
        )

        entity_tag_specification = (
            [tag_spec._asdict() for tag_spec in self._entity_tag_specs]
            if self._entity_tag_specs
            else []
        )
        convo.shared.utils.io.dump_object_as_json_to_file(
            model_directory / f"{filename}.entity_tag_specs.json", entity_tag_specification
        )

        return {"file": filename}

    @classmethod
    def load(
        cls,
        meta_data: Dict[Text, Any],
        model_dir: Text = None,
        model_metadata: Metadataset = None,
        cached_component: Optional["DIETClassifier"] = None,
        **kwargs: Any,
    ) -> "DIETClassifier":
        """Loads the trained model from the provided dir."""

        if not model_dir or not meta_data.get("file"):
            log.debug(
                f"Failed to load model for '{cls.__name__}'. "
                f"Maybe you did not provide enough training data and no model was "
                f"trained or the path '{os.path.abspath(model_dir)}' doesn't exist?"
            )
            return cls(component_config=meta_data)

        (
            index_label_id_mapping,
            entity_tag_specs,
            label_data,
            meta_data,
            data_example,
        ) = cls._load_from_files(meta_data, model_dir)

        meta_data = train_utils.updating_similarity_type(meta_data)

        fetch_model_data = cls._load_model(
            entity_tag_specs, label_data, meta_data, data_example, model_dir
        )

        return cls(
            component_config=meta_data,
            index_label_id_mapping=index_label_id_mapping,
            entity_tag_specs=entity_tag_specs,
            model=fetch_model_data,
        )

    @classmethod
    def _load_from_files(cls, meta: Dict[Text, Any], model_directory: Text):
        fetch_file_name = meta.get("file")

        model_directory = Path(model_directory)

        data_eg = io_utils.pick_load(model_directory / f"{fetch_file_name}.data_example.pkl")
        tag_data = io_utils.pick_load(model_directory / f"{fetch_file_name}.label_data.pkl")
        tag_data = ConvoModelDataSet(data=tag_data)
        indices_label_id_mapping = io_utils.json_un_pickle(
            model_directory / f"{fetch_file_name}.index_label_id_mapping.json"
        )
        entity_tag_specification = convo.shared.utils.io.reading_json_file(
            model_directory / f"{fetch_file_name}.entity_tag_specs.json"
        )
        entity_tag_specification = [
            EntityTagSpecification(
                tag_name=tag_spec["tag_name"],
                ids_to_tags={
                    int(key): value for key, value in tag_spec["ids_to_tags"].items()
                },
                tags_to_ids={
                    key: int(value) for key, value in tag_spec["tags_to_ids"].items()
                },
                num_tags=tag_spec["num_tags"],
            )
            for tag_spec in entity_tag_specification
        ]

        # jsonpickle converts dictionary keys to strings
        indices_label_id_mapping = {
            int(key): value for key, value in indices_label_id_mapping.items()
        }

        return (
            indices_label_id_mapping,
            entity_tag_specification,
            tag_data,
            meta,
            data_eg,
        )

    @classmethod
    def _load_model(
        cls,
        entity_tag_specs: List[EntityTagSpecification],
        label_data: ConvoModelDataSet,
        meta: Dict[Text, Any],
        data_example: Dict[Text, Dict[Text, List[np.ndarray]]],
        model_dir: Text,
    ) -> "ConvoModel":
        fetch_file_name = meta.get("file")
        fetch_tf_model_file = os.path.join(model_dir, fetch_file_name + ".tf_model")

        tag_keys = TAG_KEY if meta[INTENT_CLASSIFY] else None
        tag_sub_key = TAG_SUB_KEY if meta[INTENT_CLASSIFY] else None

        model_data_set_eg = ConvoModelDataSet(
            label_key=tag_keys, label_sub_key=tag_sub_key, data=data_example
        )

        fetch_model_data = cls._load_model_class(
            fetch_tf_model_file, model_data_set_eg, label_data, entity_tag_specs, meta
        )

        # build the graph for prediction
        forecast_data_set_eg = ConvoModelDataSet(
            label_key=tag_keys,
            data={
                feature_name: features
                for feature_name, features in model_data_set_eg.items()
                if TXT in feature_name
            },
        )

        fetch_model_data.build_for_prediction(forecast_data_set_eg)

        return fetch_model_data

    @classmethod
    def _load_model_class(
        cls,
        tf_model_file: Text,
        model_data_example: ConvoModelDataSet,
        label_data: ConvoModelDataSet,
        entity_tag_specs: List[EntityTagSpecification],
        meta: Dict[Text, Any],
    ) -> "ConvoModel":

        return cls.model_class().load(
            tf_model_file,
            model_data_example,
            data_signature=model_data_example.get_sign(),
            label_data=label_data,
            entity_tag_specs=entity_tag_specs,
            config=copy.deepcopy(meta),
        )

    def _instant_model_class(self, model_data: ConvoModelDataSet) -> "ConvoModel":

        return self.model_class()(
            data_signature=model_data.get_sign(),
            label_data=self._label_data,
            entity_tag_specs=self._entity_tag_specs,
            config=self.component_config,
        )


# accessing _tf_layers with any key results in key-error, disable it
# pytype: disable=key-error


class DIET(ConverterConvoModel):
    def __init__(
        self,
        data_signature: Dict[Text, Dict[Text, List[FeatureSign]]],
        label_data: ConvoModelDataSet,
        entity_tag_specs: Optional[List[EntityTagSpecification]],
        config: Dict[Text, Any],
    ) -> None:
        # create entity tag spec before calling super otherwise building the model
        # will fail
        super().__init__("DIET", config, data_signature, label_data)
        self._entity_tag_specs = self._ordered_tag_specification(entity_tag_specs)

        self.predict_data_signature = {
            feature_name: features
            for feature_name, features in data_signature.items()
            if TXT in feature_name
        }

        # tf training
        self.optimizer = tf.keras.optimizers.Adam(config[RATE_OF_LEARNING])
        self._generate_metrics()
        self._upgrade_metrics_to_log()

        self.all_labels_embed = None  # needed for efficient prediction
        self._produce_layers()

    @staticmethod
    def _ordered_tag_specification(
        entity_tag_specs: Optional[List[EntityTagSpecification]],
    ) -> List[EntityTagSpecification]:
        """Ensure that order of entity tag specs matches ConditionalRandomFields layer order."""
        if entity_tag_specs is None:
            return []

        conditional_random_fields_order = [
            ATTRIBUTE_TYPE_ENTITY,
            ATTRIBUTE_ROLE_ENTITY,
            ATTRIBUTE_GROUP_ENTITY,
        ]

        ordered_tag_specification = []

        for tag_name in conditional_random_fields_order:
            for tag_spec in entity_tag_specs:
                if tag_name == tag_spec.tag_name:
                    ordered_tag_specification.append(tag_spec)

        return ordered_tag_specification

    def _check_data(self) -> None:
        if TXT not in self.data_signature:
            raise InvalidConfigurationError(
                f"No text features specified. "
                f"Cannot train '{self.__class__.__name__}' model."
            )
        if self.config[INTENT_CLASSIFY]:
            if STAGE not in self.data_signature:
                raise InvalidConfigurationError(
                    f"No label features specified. "
                    f"Cannot train '{self.__class__.__name__}' model."
                )

            if self.config[SHARED_HIDDEN_LAYERS]:
                different_sentence_signatures = False
                different_sequence_signatures = False
                if (
                    SENTENCE in self.data_signature[TXT]
                    and SENTENCE in self.data_signature[STAGE]
                ):
                    different_sentence_signatures = (
                        self.data_signature[TXT][SENTENCE]
                        != self.data_signature[STAGE][SENTENCE]
                    )
                if (
                    SEQUENTIAL in self.data_signature[TXT]
                    and SEQUENTIAL in self.data_signature[STAGE]
                ):
                    different_sequence_signatures = (
                        self.data_signature[TXT][SEQUENTIAL]
                        != self.data_signature[STAGE][SEQUENTIAL]
                    )

                if different_sentence_signatures or different_sequence_signatures:
                    raise ValueError(
                        "If hidden layer weights are shared, data signatures "
                        "for text_features and label_features must coincide."
                    )

        if self.config[ENTITY_IDENTIFICATION] and (
            ENTITIES_NAME not in self.data_signature
            or ATTRIBUTE_TYPE_ENTITY not in self.data_signature[ENTITIES_NAME]
        ):
            log.debug(
                f"You specified '{self.__class__.__name__}' to train entities, but "
                f"no entities are present in the training data. Skipping training of "
                f"entities."
            )
            self.config[ENTITY_IDENTIFICATION] = False

    def _generate_metrics(self) -> None:
        # self.metrics will have the same order as they are created
        # so create loss metrics first to output losses first
        self.mask_loss = tf.keras.metrics.Mean(name="m_loss")
        self.intent_loss = tf.keras.metrics.Mean(name="i_loss")
        self.entity_loss = tf.keras.metrics.Mean(name="e_loss")
        self.entity_group_loss = tf.keras.metrics.Mean(name="g_loss")
        self.entity_role_loss = tf.keras.metrics.Mean(name="r_loss")
        # create accuracy metrics second to output accuracies second
        self.mask_acc = tf.keras.metrics.Mean(name="m_acc")
        self.intent_acc = tf.keras.metrics.Mean(name="i_acc")
        self.entity_f1 = tf.keras.metrics.Mean(name="e_f1")
        self.entity_group_f1 = tf.keras.metrics.Mean(name="g_f1")
        self.entity_role_f1 = tf.keras.metrics.Mean(name="r_f1")

    def _upgrade_metrics_to_log(self) -> None:
        log_level_debuging = logging.getLogger("convo").level == logging.DEBUG

        if self.config[COVERED_LM]:
            self.metrics_to_log.append("m_acc")
            if log_level_debuging:
                self.metrics_to_log.append("m_loss")
        if self.config[INTENT_CLASSIFY]:
            self.metrics_to_log.append("i_acc")
            if log_level_debuging:
                self.metrics_to_log.append("i_loss")
        if self.config[ENTITY_IDENTIFICATION]:
            for tag_spec in self._entity_tag_specs:
                if tag_spec.num_tags != 0:
                    name = tag_spec.tag_name
                    self.metrics_to_log.append(f"{name[0]}_f1")
                    if log_level_debuging:
                        self.metrics_to_log.append(f"{name[0]}_loss")

        self._log_metric_informations()

    def _log_metric_informations(self) -> None:
        fetch_metric_name = {
            "t": "total",
            "i": "intent",
            "e": "entity",
            "m": "mask",
            "r": "role",
            "g": "group",
        }
        log.debug("Following metrics will be logged during training: ")
        for metric in self.metrics_to_log:
            parts = metric.split("_")
            name = f"{fetch_metric_name[parts[0]]} {parts[1]}"
            log.debug(f"  {metric} ({name})")

    def _produce_layers(self) -> None:
        self.text_name = TXT
        self._prepare_sequence_layers(self.text_name)
        if self.config[COVERED_LM]:
            self._produce_mask_lm_layers(self.text_name)
        if self.config[INTENT_CLASSIFY]:
            self.label_name = TXT if self.config[SHARED_HIDDEN_LAYERS] else STAGE
            self._produce_input_layers(self.label_name)
            self._produce_label_classification_layers()
        if self.config[ENTITY_IDENTIFICATION]:
            self._produce_entity_recognition_layers()

    def _produce_input_layers(self, name: Text) -> None:
        self.ffnn_layer_preparation(
            name, self.config[SIZES_OF_HIDDEN_LAYERS][name], self.config[DROP_PRICE]
        )

        for feature_type in [SENTENCE, SEQUENTIAL]:
            if (
                name not in self.data_signature
                or feature_type not in self.data_signature[name]
            ):
                continue

            self.sparse_dense_dropout_layers_preparation(
                f"{name}_{feature_type}", self.config[DROP_PRICE]
            )
            self.sparse_dense_layers_preparation(
                self.data_signature[name][feature_type],
                f"{name}_{feature_type}",
                self.config[DIMENSION_DENSE][name],
            )
            self.ffnn_layer_preparation(
                f"{name}_{feature_type}",
                [self.config[CONCATENATE_DIMENSION][name]],
                self.config[DROP_PRICE],
                prefix="concat_layer",
            )

    def _prepare_sequence_layers(self, name: Text) -> None:
        self._produce_input_layers(name)
        self.transformer_layer_preparation(
            name, self.config[DROP_PRICE], self.config[ATTENTION_DROP_RATE]
        )

    def _produce_mask_lm_layers(self, name: Text) -> None:
        self._tf_layers[f"{name}_input_mask"] = layers.MaskInput()

        self.preparing_embedding_layers(f"{name}_lm_mask")
        self.preparing_embedding_layers(f"{name}_golden_token")

        # mask loss is additional loss
        # set scaling to False, so that it doesn't overpower others losses
        self.dot_product_loss_preparation(f"{name}_mask", scale_loss=False)

    def _produce_label_classification_layers(self) -> None:
        self.preparing_embedding_layers(TXT)
        self.preparing_embedding_layers(STAGE)

        self.dot_product_loss_preparation(STAGE, self.config[LOSS_SCALE])

    def _produce_entity_recognition_layers(self) -> None:
        for tag_spec in self._entity_tag_specs:
            name = tag_spec.tag_name
            num_tags = tag_spec.num_tags
            self._tf_layers[f"embed.{name}.logits"] = layers.implanted(
                num_tags, self.config[REGULARIZATION_CONST], f"logits.{name}"
            )
            self._tf_layers[f"crf.{name}"] = layers.ConditionalRandomFields(
                num_tags, self.config[REGULARIZATION_CONST], self.config[LOSS_SCALE]
            )
            self._tf_layers[f"embed.{name}.tags"] = layers.implanted(
                self.config[EMBEDDING_CAPACITY],
                self.config[REGULARIZATION_CONST],
                f"tags.{name}",
            )

    def _features_as_sequence_ids(
        self, features: List[Union[np.ndarray, tf.Tensor, tf.SparseTensor]], name: Text
    ) -> Optional[tf.Tensor]:
        """Creates dense labels for negative sampling."""

        # if there are dense features - we can use them
        for f in features:
            if not isinstance(f, tf.SparseTensor):
                seq_ids = tf.stop_gradient(f)
                # add a zero to the seq dimension for the sentence features
                seq_ids = tf.pad(seq_ids, [[0, 0], [0, 1], [0, 0]])
                return seq_ids

        # use additional sparse to dense layer
        for f in features:
            if isinstance(f, tf.SparseTensor):
                seq_ids = tf.stop_gradient(
                    self._tf_layers[f"sparse_to_dense_ids.{name}"](f)
                )
                # add a zero to the seq dimension for the sentence features
                seq_ids = tf.pad(seq_ids, [[0, 0], [0, 1], [0, 0]])
                return seq_ids

        return None

    def _merge_sequence_sentence_features(
        self,
        sequence_features: List[Union[tf.Tensor, tf.SparseTensor]],
        sentence_features: List[Union[tf.Tensor, tf.SparseTensor]],
        mask_sequence: tf.Tensor,
        mask_text: tf.Tensor,
        name: Text,
        sparse_dropout: bool = False,
        dense_dropout: bool = False,
    ) -> tf.Tensor:
        seq_x = self._combine_sparse_dense_features(
            sequence_features,
            f"{name}_{SEQUENTIAL}",
            mask_sequence,
            sparse_dropout,
            dense_dropout,
        )
        statement_x = self._combine_sparse_dense_features(
            sentence_features, f"{name}_{SENTENCE}", None, sparse_dropout, dense_dropout
        )

        if seq_x is not None and statement_x is None:
            return seq_x

        if seq_x is None and statement_x is not None:
            return statement_x

        if seq_x is not None and statement_x is not None:
            return self._concat_seq_sentence_features(
                seq_x, statement_x, name, mask_text
            )

        raise ValueError(
            "No features are present. Please check your configuration file."
        )

    def _concat_seq_sentence_features(
        self,
        seq_x: tf.Tensor,
        statement_x: tf.Tensor,
        name: Text,
        mask_text: tf.Tensor,
    ):
        if seq_x.shape[-1] != statement_x.shape[-1]:
            seq_x = self._tf_layers[f"concat_layer.{name}_{SEQUENTIAL}"](
                seq_x, self._training
            )
            statement_x = self._tf_layers[f"concat_layer.{name}_{SENTENCE}"](
                statement_x, self._training
            )

        # we need to concatenate the sequence features with the sentence features
        # we cannot use tf.concat as the sequence features are padded

        # (1) get position of sentence features in mask
        end = mask_text * tf.math.cumprod(
            1 - mask_text, axis=1, exclusive=True, reverse=True
        )
        # (2) multiply by sentence features so that we get a matrix of
        #     batch-dim x seq-dim x feature-dim with zeros everywhere except for
        #     for the sentence features
        statement_x = end * statement_x

        # (3) add a zero to the end of sequence matrix to match the final shape
        seq_x = tf.pad(seq_x, [[0, 0], [0, 1], [0, 0]])

        # (4) sum up sequence features and sentence features
        return seq_x + statement_x

    def _generate_bow(
        self,
        sequence_features: List[Union[tf.Tensor, tf.SparseTensor]],
        sentence_features: List[Union[tf.Tensor, tf.SparseTensor]],
        sequence_mask: tf.Tensor,
        text_mask: tf.Tensor,
        name: Text,
        sparse_dropout: bool = False,
        dense_dropout: bool = False,
    ) -> tf.Tensor:

        y = self._merge_sequence_sentence_features(
            sequence_features,
            sentence_features,
            sequence_mask,
            text_mask,
            name,
            sparse_dropout,
            dense_dropout,
        )
        y = tf.reduce_sum(y, axis=1)  # convert to bag-of-words
        return self._tf_layers[f"ffnn.{name}"](y, self._training)

    def _create_sequence(
        self,
        sequence_features: List[Union[tf.Tensor, tf.SparseTensor]],
        sentence_features: List[Union[tf.Tensor, tf.SparseTensor]],
        mask_sequence: tf.Tensor,
        mask: tf.Tensor,
        name: Text,
        sparse_dropout: bool = False,
        dense_dropout: bool = False,
        masked_lm_loss: bool = False,
        sequence_ids: bool = False,
    ) -> Tuple[tf.Tensor, tf.Tensor, Optional[tf.Tensor], Optional[tf.Tensor]]:
        if sequence_ids:
            sequence_ids = self._features_as_sequence_ids(sequence_features, f"{name}_{SEQUENTIAL}")
        else:
            sequence_ids = None

        put_in = self._merge_sequence_sentence_features(
            sequence_features,
            sentence_features,
            mask_sequence,
            mask,
            name,
            sparse_dropout,
            dense_dropout,
        )
        put_in = self._tf_layers[f"ffnn.{name}"](put_in, self._training)

        if masked_lm_loss:
            inputs_transformer, lm_mask_boolean = self._tf_layers[f"{name}_input_mask"](
                put_in, mask, self._training
            )
        else:
            inputs_transformer = put_in
            lm_mask_boolean = None

        results = self._tf_layers[f"transformer.{name}"](
            inputs_transformer, 1 - mask, self._training
        )

        if self.config[NUMBER_TRANSFORMER_LAYERS] > 0:
            # apply activation
            results = tfa.activations.gelu(results)

        return results, put_in, sequence_ids, lm_mask_boolean

    def _generate_all_labels(self) -> Tuple[tf.Tensor, tf.Tensor]:
        all_tag_ids = self.tf_label_data[TAG_KEY][TAG_SUB_KEY][0]

        mask_seq_label = self.getting_mask(
            self.tf_label_data, STAGE, SEQUENCE_LEN
        )

        x = self._generate_bow(
            self.tf_label_data[STAGE][SEQUENTIAL],
            self.tf_label_data[STAGE][SENTENCE],
            mask_seq_label,
            mask_seq_label,
            self.label_name,
        )
        all_labels_embed = self._tf_layers[f"embed.{STAGE}"](x)

        return all_tag_ids, all_labels_embed

    def _mask_loss(
        self,
        results: tf.Tensor,
        put_in: tf.Tensor,
        seq_ids: tf.Tensor,
        lm_mask_boolean: tf.Tensor,
        name: Text,
    ) -> tf.Tensor:
        # make sure there is at least one element in the mask
        lm_mask_boolean = tf.cond(
            tf.reduce_any(lm_mask_boolean),
            lambda: lm_mask_boolean,
            lambda: tf.scatter_nd([[0, 0, 0]], [True], tf.shape(lm_mask_boolean)),
        )

        lm_mask_boolean = tf.squeeze(lm_mask_boolean, -1)
        # pick elements that were masked
        results = tf.boolean_mask(results, lm_mask_boolean)
        put_in = tf.boolean_mask(put_in, lm_mask_boolean)
        identity = tf.boolean_mask(seq_ids, lm_mask_boolean)

        results_combined = self._tf_layers[f"embed.{name}_lm_mask"](results)
        inputs_combined = self._tf_layers[f"embed.{name}_golden_token"](put_in)

        return self._tf_layers[f"loss.{name}_mask"](
            results_combined, inputs_combined, identity, inputs_combined, identity
        )

    def _compute_label_loss(
        self, text_features: tf.Tensor, label_features: tf.Tensor, label_ids: tf.Tensor
    ) -> tf.Tensor:
        all_tag_ids, all_tags_combined = self._generate_all_labels()

        txt_combined = self._tf_layers[f"embed.{TXT}"](text_features)
        tag_combined = self._tf_layers[f"embed.{STAGE}"](label_features)

        return self._tf_layers[f"loss.{STAGE}"](
            txt_combined, tag_combined, label_ids, all_tags_combined, all_tag_ids
        )

    def _compute_entity_loss(
        self,
        put_in: tf.Tensor,
        label_ids: tf.Tensor,
        mask: tf.Tensor,
        sequence_lengths: tf.Tensor,
        tag_name: Text,
        entity_tags: Optional[tf.Tensor] = None,
    ) -> Tuple[tf.Tensor, tf.Tensor, tf.Tensor]:

        label_ids = tf.cast(label_ids[:, :, 0], tf.int32)

        if entity_tags is not None:
            _labels = self._tf_layers[f"embed.{tag_name}.tags"](entity_tags)
            put_in = tf.concat([put_in, _labels], axis=-1)

        logins = self._tf_layers[f"embed.{tag_name}.logits"](put_in)

        # should call first to build weights
        pred_identity, _ = self._tf_layers[f"crf.{tag_name}"](logins, sequence_lengths)
        # pytype cannot infer that 'self._tf_layers["crf"]' has the method '.loss'
        # pytype: disable=attribute-error
        losses = self._tf_layers[f"crf.{tag_name}"].data_loss(
            logins, label_ids, sequence_lengths
        )
        f1_key = self._tf_layers[f"crf.{tag_name}"].f1_score(label_ids, pred_identity, mask)
        # pytype: enable=attribute-error

        return losses, f1_key, logins

    @staticmethod
    def _get_sequence_lengths(
        tf_batch_data: Dict[Text, Dict[Text, List[tf.Tensor]]],
        key: Text,
        sub_key: Text,
        batch_dim: int = 1,
    ) -> tf.Tensor:
        # sentence features have a sequence lengths of 1
        # if sequence features are present we add the sequence lengths of those

        seq_len = tf.ones([batch_dim], dtype=tf.int32)
        if key in tf_batch_data and sub_key in tf_batch_data[key]:
            seq_len += tf.cast(tf_batch_data[key][sub_key][0], dtype=tf.int32)

        return seq_len

    @staticmethod
    def _fetch_batch_dim(tf_batch_data: Dict[Text, Dict[Text, List[tf.Tensor]]]) -> int:
        if TXT in tf_batch_data and SEQUENTIAL in tf_batch_data[TXT]:
            return tf.shape(tf_batch_data[TXT][SEQUENTIAL][0])[0]

        return tf.shape(tf_batch_data[TXT][SENTENCE][0])[0]

    def batch_loss(
        self, batch_in: Union[Tuple[tf.Tensor], Tuple[np.ndarray]]
    ) -> tf.Tensor:
        fetch_tf_batch_data = self.batch_to_model_data_set_format(batch_in, self.data_signature)

        dim_batch = self._fetch_batch_dim(fetch_tf_batch_data)
        mask_seq_txt = self.getting_mask(fetch_tf_batch_data, TXT, SEQUENCE_LEN)
        seq_len = self._get_sequence_lengths(
            fetch_tf_batch_data, TXT, SEQUENCE_LEN, dim_batch
        )
        mask_txt = self.computing_mask(seq_len)

        (
            text_transformed,
            text_in,
            text_seq_ids,
            lm_mask_bool_text,
        ) = self._create_sequence(
            fetch_tf_batch_data[TXT][SEQUENTIAL],
            fetch_tf_batch_data[TXT][SENTENCE],
            mask_seq_txt,
            mask_txt,
            self.text_name,
            sparse_dropout=self.config[SPARSE_INP_DROP_OUT],
            dense_dropout=self.config[DENSE_INP_DROP_OUT],
            masked_lm_loss=self.config[COVERED_LM],
            sequence_ids=True,
        )

        loss_ = []

        if self.config[COVERED_LM]:
            losses_, account = self._mask_loss(
                text_transformed, text_in, text_seq_ids, lm_mask_bool_text, TXT
            )
            self.mask_loss.update_state(losses_)
            self.mask_acc.update_state(account)
            loss_.append(losses_)

        if self.config[INTENT_CLASSIFY]:
            losses_ = self._loss_of_batches_intent(
                seq_len, mask_txt, text_transformed, fetch_tf_batch_data
            )
            loss_.append(losses_)

        if self.config[ENTITY_IDENTIFICATION]:
            loss_ += self._loss_of_batches_entities(
                mask_txt, seq_len, text_transformed, fetch_tf_batch_data
            )

        return tf.math.add_n(loss_)

    def _loss_of_batches_intent(
        self,
        sequence_lengths: tf.Tensor,
        mask_text: tf.Tensor,
        text_transformed: tf.Tensor,
        tf_batch_data: Dict[Text, Dict[Text, List[tf.Tensor]]],
    ) -> tf.Tensor:
        # get sentence features vector for intent classification
        statement_vector = self.end_token(text_transformed, sequence_lengths)

        mask_seq_label = self.getting_mask(tf_batch_data, STAGE, SEQUENCE_LEN)

        tag_ids = tf_batch_data[TAG_KEY][TAG_SUB_KEY][0]
        tag = self._generate_bow(
            tf_batch_data[STAGE][SEQUENTIAL],
            tf_batch_data[STAGE][SENTENCE],
            mask_seq_label,
            mask_text,
            self.label_name,
        )

        losses, account = self._compute_label_loss(statement_vector, tag, tag_ids)

        self._upgrade_label_metrics(losses, account)

        return losses

    def _upgrade_label_metrics(self, loss: tf.Tensor, acc: tf.Tensor) -> None:

        self.intent_loss.update_state(loss)
        self.intent_acc.update_state(acc)

    def _loss_of_batches_entities(
        self,
        mask_text: tf.Tensor,
        seq_len: tf.Tensor,
        text_transformed: tf.Tensor,
        tf_batch_data: Dict[Text, Dict[Text, List[tf.Tensor]]],
    ) -> List[tf.Tensor]:
        losses = []

        seq_len -= 1  # remove sentence features

        entity_labels = None

        for tag_spec in self._entity_tag_specs:
            if tag_spec.num_tags == 0:
                continue

            tag_ids = tf_batch_data[ENTITIES_NAME][tag_spec.tag_name][0]
            # add a zero (no entity) for the sentence features to match the shape of
            # inputs
            tag_ids = tf.pad(tag_ids, [[0, 0], [0, 1], [0, 0]])

            loss, f1_key, _logins = self._compute_entity_loss(
                text_transformed,
                tag_ids,
                mask_text,
                seq_len,
                tag_spec.tag_name,
                entity_labels,
            )

            if tag_spec.tag_name == ATTRIBUTE_TYPE_ENTITY:
                # use the entity tags as additional input for the role
                # and group ConditionalRandomFields
                entity_labels = tf.one_hot(
                    tf.cast(tag_ids[:, :, 0], tf.int32), depth=tag_spec.num_tags
                )

            self._upgrade_entity_metrics(loss, f1_key, tag_spec.tag_name)

            losses.append(loss)

        return losses

    def _upgrade_entity_metrics(self, loss: tf.Tensor, f1: tf.Tensor, tag_name: Text):
        if tag_name == ATTRIBUTE_TYPE_ENTITY:
            self.entity_loss.update_state(loss)
            self.entity_f1.update_state(f1)
        elif tag_name == ATTRIBUTE_GROUP_ENTITY:
            self.entity_group_loss.update_state(loss)
            self.entity_group_f1.update_state(f1)
        elif tag_name == ATTRIBUTE_ROLE_ENTITY:
            self.entity_role_loss.update_state(loss)
            self.entity_role_f1.update_state(f1)

    def batch_predict(
        self, batch_in: Union[Tuple[tf.Tensor], Tuple[np.ndarray]]
    ) -> Dict[Text, tf.Tensor]:
        fetch_tf_batch_data = self.batch_to_model_data_set_format(
            batch_in, self.predict_data_signature
        )

        mask_seq_txt = self.getting_mask(fetch_tf_batch_data, TXT, SEQUENCE_LEN)
        seq_len = self._get_sequence_lengths(
            fetch_tf_batch_data, TXT, SEQUENCE_LEN, batch_dim=1
        )

        face = self.computing_mask(seq_len)

        text_transformed, _, _, _ = self._create_sequence(
            fetch_tf_batch_data[TXT][SEQUENTIAL],
            fetch_tf_batch_data[TXT][SENTENCE],
            mask_seq_txt,
            face,
            self.text_name,
        )

        predictions: Dict[Text, tf.Tensor] = {}

        if self.config[INTENT_CLASSIFY]:
            predictions.update(
                self._batch_predict_convo_intents(seq_len, text_transformed)
            )

        if self.config[ENTITY_IDENTIFICATION]:
            predictions.update(
                self._batch_forecast_intents(seq_len, text_transformed)
            )

        return predictions

    def _batch_forecast_intents(
        self, sequence_lengths: tf.Tensor, text_transformed: tf.Tensor
    ) -> Dict[Text, tf.Tensor]:
        predictions: Dict[Text, tf.Tensor] = {}

        entity_labels = None

        for tag_spec in self._entity_tag_specs:
            # skip crf layer if it was not trained
            if tag_spec.num_tags == 0:
                continue

            fetch_name = tag_spec.tag_name
            _put_in = text_transformed

            if entity_labels is not None:
                _labels = self._tf_layers[f"embed.{fetch_name}.tags"](entity_labels)
                _put_in = tf.concat([_put_in, _labels], axis=-1)

            _logits = self._tf_layers[f"embed.{fetch_name}.logits"](_put_in)
            pred_identity, confidences = self._tf_layers[f"crf.{fetch_name}"](
                _logits, sequence_lengths - 1
            )

            predictions[f"e_{fetch_name}_ids"] = pred_identity
            predictions[f"e_{fetch_name}_scores"] = confidences

            if fetch_name == ATTRIBUTE_TYPE_ENTITY:
                # use the entity tags as additional input for the role
                # and group ConditionalRandomFields
                entity_labels = tf.one_hot(
                    tf.cast(pred_identity, tf.int32), depth=tag_spec.num_tags
                )

        return predictions

    def _batch_predict_convo_intents(
        self, sequence_lengths: tf.Tensor, text_transformed: tf.Tensor
    ) -> Dict[Text, tf.Tensor]:

        if self.all_labels_embed is None:
            _, self.all_labels_embed = self._generate_all_labels()

        # get sentence feature vector for intent classification
        statement_vector = self.end_token(text_transformed, sequence_lengths)
        statement_vector_embed = self._tf_layers[f"embed.{TXT}"](statement_vector)

        # pytype cannot infer that 'self._tf_layers[f"loss.{STAGE}"]' has methods
        # like '.sim' or '.confidence_from_sim'
        # pytype: disable=attribute-error
        sim_all = self._tf_layers[f"loss.{STAGE}"].simulation(
            statement_vector_embed[:, tf.newaxis, :],
            self.all_labels_embed[tf.newaxis, :, :],
        )
        result = self._tf_layers[f"loss.{STAGE}"].confidence_from_simulation(
            sim_all, self.config[SIMILARITY_TYPE_CATEGORY]
        )
        # pytype: enable=attribute-error

        return {"i_scores": result}


# pytype: enable=key-error
