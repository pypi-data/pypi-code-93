import copy
import logging

import numpy as np
import tensorflow as tf

from typing import Any, Dict, Optional, Text, Tuple, Union, List, Type

from convo.shared.nlu.training_data import util
import convo.shared.utils.io
from convo.nlu.config import InvalidConfigurationError
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
from convo.nlu.components import Element
from convo.nlu.featurizers.featurizer import Featurizer
from convo.nlu.model import Metadataset
from convo.nlu.classifiers.diet_classifier import (
    DIETClassifier,
    DIET,
    TAG_KEY,
    TAG_SUB_KEY,
    EntityTagSpecification,
    SEQUENCE_LEN,
    SENTENCE,
    SEQUENTIAL,
)
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
    RETRIEVAL_INTENT,
    USE_TEXT_AS_LABEL,
    SOFT_MAX,
    AUTOMATIC,
    BALANCED_VALUE,
    TENSOR_BOARD_LOG_DIRECTORY,
    TENSOR_BOARD_LOGGING_LEVEL,
    CONCATENATE_DIMENSION,
    FEATURES,
    CHECK_POINT_MODEL,
    DIMENSION_DENSE,
)
from convo.nlu.constants import (
    PROP_NAME_RESPONSE_PICKER,
    RETRIEVE_INTENTS_RESPONSE_PICKER,
    RESP_KEY_RESPONSE_PICKER,
    PREDICTION_KEY_RESPONSE_PICKER,
    RANK_KEY_RESPONSE_PICKER,
    TEMPLATE_NAME_KEY_RESPONSE_PICKER,
    DFAULT_INTENT_RESPONSE_PICKER,
)
from convo.shared.nlu.constants import (
    TXT,
    INTENTION,
    RETURN_RESPONSE,
    KEY_INTENT_RESPONSE,
    KEY_INTENT_NAME,
    KEY_PREDICTED_CONFIDENCE,
)

from convo.utils.tensorflow.model_data import ConvoModelDataSet
from convo.utils.tensorflow.models import ConvoModel

log = logging.getLogger(__name__)


class ResponseSelector(DIETClassifier):
    """Response selector using supervised embeddings.

    The response selector embeds user inputs
    and candidate response into the same space.
    Supervised embeddings are trained by maximizing similarity between them.
    It also provides rankings of the response that did not "win".

    The supervised response selector needs to be preceded by
    a featurizer in the pipeline.
    This featurizer creates the features used for the embeddings.
    It is recommended to use ``CountVectorsFeaturizer`` that
    can be optionally preceded by ``SpacyNLP`` and ``SpacyTokenizer``.

    Based on the starspace idea from: https://arxiv.org/abs/1709.03856.
    However, in this implementation the `mu` parameter is treated differently
    and additional hidden layers are added together with dropout.
    """

    @classmethod
    def required_components(cls) -> List[Type[Element]]:
        return [Featurizer]

    defaults = {
        # ## Architecture of the used neural network
        # Hidden layer sizes for layers before the embedding layers for user message
        # and labels.
        # The number of hidden layers is equal to the length of the corresponding
        # list.
        SIZES_OF_HIDDEN_LAYERS: {TXT: [256, 128], STAGE: [256, 128]},
        # Whether to share the hidden layer weights between input words and responses
        SHARED_HIDDEN_LAYERS: False,
        # Number of units in transformer
        TRANSFORMER_DIMENSION: None,
        # Number of transformer layers
        NUMBER_TRANSFORMER_LAYERS: 0,
        # Number of attention heads in transformer
        NUMBER_HEADS: 4,
        # If 'True' use key relative embeddings in attention
        RELATIVE_ATTENTION_KEY: False,
        # If 'True' use key relative embeddings in attention
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
        DIMENSION_DENSE: {TXT: 512, STAGE: 512},
        # Default dimension to use for concatenating sequence and sentence features.
        CONCATENATE_DIMENSION: {TXT: 512, STAGE: 512},
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
        # Scale loss inverse proportionally to confidence of correct prediction
        LOSS_SCALE: True,
        # ## Regularization parameters
        # The scale of regularization
        REGULARIZATION_CONST: 0.002,
        # Sparsity of the weights in dense layers
        WEIGHT_SPARSE: 0.0,
        # The scale of how important is to minimize the maximum similarity
        # between embeddings of different labels.
        NEG_MARGIN_SCALE: 0.8,
        # Dropout rate for encoder
        DROP_PRICE: 0.2,
        # Dropout rate for attention
        ATTENTION_DROP_RATE: 0,
        # If 'True' apply dropout to sparse input tensors
        SPARSE_INP_DROP_OUT: False,
        # If 'True' apply dropout to dense input tensors
        DENSE_INP_DROP_OUT: False,
        # ## Evaluation parameters
        # How often calculate validation accuracy.
        # Small values may hurt performance, e.g. model accuracy.
        EVALUATE_NUMBER_EPOCHS: 20,
        # How many examples to use for hold out validation set
        # Large values may hurt performance, e.g. model accuracy.
        EVALUATE_NUM_EXAMPLES: 0,
        # ## Selector config
        # If 'True' random tokens of the input message will be masked and the model
        # should predict those tokens.
        COVERED_LM: False,
        # Name of the intent for which this response selector is to be trained
        RETRIEVAL_INTENT: None,
        # Boolean flag to check if actual text of the response
        # should be used as ground truth label for training the model.
        USE_TEXT_AS_LABEL: False,
        # If you want to use tensorboard to visualize training and validation metrics,
        # set this option to a valid output dir.
        TENSOR_BOARD_LOG_DIRECTORY: None,
        # Define when training metrics for tensorboard should be logged.
        # Either after every epoch or for every training step.
        # Valid values: 'epoch' and 'minibatch'
        TENSOR_BOARD_LOGGING_LEVEL: "epoch",
        # Specify what features to use as sequence and sentence features
        # By default all features in the pipeline are used.
        FEATURES: [],
        # Perform model checkpointing
        CHECK_POINT_MODEL: False,
    }

    def __init__(
        self,
        component_config: Optional[Dict[Text, Any]] = None,
        index_label_id_mapping: Optional[Dict[int, Text]] = None,
        entity_tag_specs: Optional[List[EntityTagSpecification]] = None,
        model: Optional[ConvoModel] = None,
        all_convo_intents_retrieval: Optional[List[Text]] = None,
        responses: Optional[Dict[Text, List[Dict[Text, Any]]]] = None,
    ) -> None:

        component_config = component_config or {}

        # the following properties cannot be adapted for the ResponseSelector
        component_config[INTENT_CLASSIFY] = True
        component_config[ENTITY_IDENTIFICATION] = False
        component_config[FLAG_BILOU] = None

        # Initialize defaults
        self.responses = responses or {}
        self.all_convo_intents_retrieval = all_convo_intents_retrieval or []
        self.retrieval_intent = None
        self.use_text_as_label = False

        super().__init__(
            component_config, index_label_id_mapping, entity_tag_specs, model
        )

    @property
    def lab_key(self) -> Text:
        return TAG_KEY

    @property
    def lab_sub_key(self) -> Text:
        return TAG_SUB_KEY

    @staticmethod
    def model_class(use_text_as_label: bool) -> Type[ConvoModel]:
        if use_text_as_label:
            return DIET_2_DIET
        else:
            return DIET2_BOW

    def _load_select_params(self, config: Dict[Text, Any]) -> None:
        self.retrieval_intent = config[RETRIEVAL_INTENT]
        self.use_text_as_label = config[USE_TEXT_AS_LABEL]

    def _check_config_params(self) -> None:
        super()._check_config_params()
        self._load_select_params(self.component_config)

    def _update_message_property(
        self, message: Msg, prediction_dict: Dict[Text, Any], selector_key: Text
    ) -> None:
        mess_selector_prop = message.get(PROP_NAME_RESPONSE_PICKER, {})
        mess_selector_prop[
            RETRIEVE_INTENTS_RESPONSE_PICKER
        ] = self.all_convo_intents_retrieval
        mess_selector_prop[selector_key] = prediction_dict
        message.put(
            PROP_NAME_RESPONSE_PICKER,
            mess_selector_prop,
            add_to_output=True,
        )

    def preprocess_train_data(self, train: TrainingDataSet) -> ConvoModelDataSet:
        """Prepares data for training.

        Performs sanity checks on training data, extracts encodings for labels.
        """

        if self.retrieval_intent:
            train = train.filtering_training_exps(
                lambda ex: self.retrieval_intent == ex.get(INTENTION)
            )
        else:
            # retrieval intent was left to its default value
            log.info(
                "Retrieval intent parameter was left to its default value. This "
                "response selector will be trained on training examples combining "
                "all retrieval convo_intents."
            )

        tag_attribute = RETURN_RESPONSE if self.use_text_as_label else KEY_INTENT_RESPONSE

        label_id_idx_map = self._label_id_indices_mapping(
            train, attribute=tag_attribute
        )

        self.responses = train.responses
        self.all_convo_intents_retrieval = list(train.retrieval_intents)

        if not label_id_idx_map:
            # no labels are present to train
            return ConvoModelDataSet()

        self.index_label_id_mapping = self._invert_mapping(label_id_idx_map)

        self._label_data = self._create_label_data(
            train, label_id_idx_map, attribute=tag_attribute
        )

        model_data_set = self._create_model_data(
            train.intent_exp,
            label_id_idx_map,
            label_attribute=tag_attribute,
        )

        self._check_input_dimension_consistency(model_data_set)

        return model_data_set

    def _resolve_intent_resp_key(
        self, label: Dict[Text, Optional[Text]]
    ) -> Optional[Text]:
        """Given a label, return the response key based on the label id.

        Args:
            label: predicted label by the selector

        Returns:
            The match for the label that was found in the known responses.
            It is always guaranteed to have a match, otherwise that case should have been caught
            earlier and a warning should have been raised.
        """

        for key, responses in self.responses.items():

            # First check if the predicted label was the key itself
            find_key = util.template_key_to_intents_response_key(key)
            if hash(find_key) == label.get("id"):
                return find_key

            # Otherwise loop over the responses to check if the text has a direct match
            for response in responses:
                if hash(response.get(TXT, "")) == label.get("id"):
                    return find_key
        return None

    def process(self, message: Msg, **kwargs: Any) -> None:
        """Return the most likely response, the associated intent_response_key and its similarity to the input."""

        outer = self._forecast(message)
        upper_label, label_rank = self._forecast_tag(outer)

        # Get the exact intent_response_key and the associated
        # response templates for the top predicted label
        label_intent_resp_key = (
                self._resolve_intent_resp_key(upper_label) or upper_label[KEY_INTENT_NAME]
        )
        label_resp_template = self.responses.get(
            util.intents_response_key_to_template_key(label_intent_resp_key)
        )

        if label_intent_resp_key and not label_resp_template:
            # response templates seem to be unavailable,
            # likely an issue with the training data
            # we'll use a fallback instead
            convo.shared.utils.io.raising_warning(
                f"Unable to fetch response templates for {label_intent_resp_key} "
                f"This means that there is likely an issue with the training data."
                f"Please make sure you have added response templates for this intent."
            )
            label_resp_template = [{TXT: label_intent_resp_key}]

        for label in label_rank:
            label[KEY_INTENT_RESPONSE] = (
                    self._resolve_intent_resp_key(label) or label[KEY_INTENT_NAME]
            )
            # Remove the "name" key since it is either the same as
            # "intent_response_key" or it is the response text which
            # is not needed in the ranking.
            label.pop(KEY_INTENT_NAME)

        selector_key = (
            self.retrieval_intent
            if self.retrieval_intent
            else DFAULT_INTENT_RESPONSE_PICKER
        )

        log.debug(
            f"Adding following selector key to message property: {selector_key}"
        )

        predict_dict = {
            PREDICTION_KEY_RESPONSE_PICKER: {
                "id": upper_label["id"],
                RESP_KEY_RESPONSE_PICKER: label_resp_template,
                KEY_PREDICTED_CONFIDENCE: upper_label[KEY_PREDICTED_CONFIDENCE],
                KEY_INTENT_RESPONSE: label_intent_resp_key,
                TEMPLATE_NAME_KEY_RESPONSE_PICKER: util.intents_response_key_to_template_key(
                    label_intent_resp_key
                ),
            },
            RANK_KEY_RESPONSE_PICKER: label_rank,
        }

        self._update_message_property(message, predict_dict, selector_key)

    def persist(self, filename: Text, model_dir: Text) -> Dict[Text, Any]:
        """Persist this model into the passed dir.

        Return the metadata necessary to load the model again.
        """
        if self.model is None:
            return {"file": None}

        super().persist(filename, model_dir)

        return {
            "file": filename,
            "responses": self.responses,
            "all_convo_intents_retrieval": self.all_convo_intents_retrieval,
        }

    @classmethod
    def _load_model_class(
        cls,
        tf_model_file: Text,
        model_data_example: ConvoModelDataSet,
        label_data: ConvoModelDataSet,
        entity_tag_specs: List[EntityTagSpecification],
        meta: Dict[Text, Any],
    ) -> "ConvoModel":
        return cls.model_class(meta[USE_TEXT_AS_LABEL]).load(
            tf_model_file,
            model_data_example,
            data_signature=model_data_example.get_sign(),
            label_data=label_data,
            entity_tag_specs=entity_tag_specs,
            config=copy.deepcopy(meta),
        )

    def _instant_model_class(self, model_data: ConvoModelDataSet) -> "ConvoModel":

        return self.model_class(self.use_text_as_label)(
            data_signature=model_data.get_sign(),
            label_data=self._label_data,
            entity_tag_specs=self._entity_tag_specs,
            config=self.component_config,
        )

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Text = None,
        model_metadata: Metadataset = None,
        cached_component: Optional["ResponseSelector"] = None,
        **kwargs: Any,
    ) -> "ResponseSelector":
        """Loads the trained model from the provided dir."""

        fetch_model = super().load(
            meta, model_dir, model_metadata, cached_component, **kwargs
        )
        if not meta.get("file"):
            return fetch_model  # pytype: disable=bad-return-type

        fetch_model.responses = meta.get("responses", {})
        fetch_model.all_convo_intents_retrieval = meta.get("all_convo_intents_retrieval", [])

        return fetch_model  # pytype: disable=bad-return-type


class DIET2_BOW(DIET):
    def _add_new_metrics(self) -> None:
        # self.metrics preserve order
        # output losses first
        self.mask_loss = tf.keras.metrics.Mean(name="m_loss")
        self.response_loss = tf.keras.metrics.Mean(name="r_loss")
        # output accuracies second
        self.mask_acc = tf.keras.metrics.Mean(name="m_acc")
        self.response_acc = tf.keras.metrics.Mean(name="r_acc")

    def _renew_metrics_to_log(self) -> None:
        find_log_level = logging.getLogger("convo").level == logging.DEBUG

        if self.config[COVERED_LM]:
            self.metrics_to_log.append("m_acc")
            if find_log_level:
                self.metrics_to_log.append("m_loss")

        self.metrics_to_log.append("r_acc")
        if find_log_level:
            self.metrics_to_log.append("r_loss")

        self._log_metric_infomation()

    def _log_metric_infomation(self) -> None:
        response_selector_metric_name = {"t": "total", "m": "mask", "r": "response"}
        log.debug("Following metrics will be logged during training: ")
        for metric in self.metrics_to_log:
            part = metric.split("_")
            response_selector_name = f"{response_selector_metric_name[part[0]]} {part[1]}"
            log.debug(f"  {metric} ({response_selector_name})")

    def _renew_label_metrics(self, loss: tf.Tensor, acc: tf.Tensor) -> None:

        self.response_loss.update_state(loss)
        self.response_acc.update_state(acc)


class DIET_2_DIET(DIET):
    def _check_data(self) -> None:
        if TXT not in self.data_signature:
            raise InvalidConfigurationError(
                f"No text features specified. "
                f"Cannot train '{self.__class__.__name__}' model."
            )
        if STAGE not in self.data_signature:
            raise InvalidConfigurationError(
                f"No label features specified. "
                f"Cannot train '{self.__class__.__name__}' model."
            )
        if (
            self.config[SHARED_HIDDEN_LAYERS]
            and self.data_signature[TXT][SENTENCE]
            != self.data_signature[STAGE][SENTENCE]
        ):
            raise ValueError(
                "If hidden layer weights are shared, data signatures "
                "for text_features and label_features must coincide."
            )

    def _add_new_metrics(self) -> None:
        # self.metrics preserve order
        # output losses first
        self.mask_loss = tf.keras.metrics.Mean(name="m_loss")
        self.response_loss = tf.keras.metrics.Mean(name="r_loss")
        # output accuracies second
        self.mask_acc = tf.keras.metrics.Mean(name="m_acc")
        self.response_acc = tf.keras.metrics.Mean(name="r_acc")

    def _renew_metrics_to_log(self) -> None:
        find_log_level = logging.getLogger("convo").level == logging.DEBUG

        if self.config[COVERED_LM]:
            self.metrics_to_log.append("m_acc")
            if find_log_level:
                self.metrics_to_log.append("m_loss")

        self.metrics_to_log.append("r_acc")
        if find_log_level:
            self.metrics_to_log.append("r_loss")

        self._log_metric_infomation()

    def _log_metric_infomation(self) -> None:
        response_selector_metric_name = {"t": "total", "m": "mask", "r": "response"}
        log.debug("Following metrics will be logged during training: ")
        for metric in self.metrics_to_log:
            parts = metric.split("_")
            response_selector_name = f"{response_selector_metric_name[parts[0]]} {parts[1]}"
            log.debug(f"  {metric} ({response_selector_name})")

    def _create_layers(self) -> None:
        self.text_name = TXT
        self.label_name = TXT if self.config[SHARED_HIDDEN_LAYERS] else STAGE

        self._prepare_sequence_layers(self.text_name)
        self._prepare_sequence_layers(self.label_name)
        if self.config[COVERED_LM]:
            self._prepare_mask_lm_layers(self.text_name)
        self._prepare_label_classification_layers()

    def _make_all_labels(self) -> Tuple[tf.Tensor, tf.Tensor]:
        all_tag_ids = self.tf_label_data[TAG_KEY][TAG_SUB_KEY][0]

        seq_mask_label = super().getting_mask(
            self.tf_label_data, STAGE, SEQUENCE_LEN
        )
        group_dim = tf.shape(self.tf_label_data[TAG_KEY][TAG_SUB_KEY][0])[0]
        seq_lengths_label = self._get_sequence_lengths(
            self.tf_label_data, STAGE, SEQUENCE_LEN, group_dim
        )
        tags_mask = self.computing_mask(seq_lengths_label)

        tag_transform, _, _, _ = self._create_sequence(
            self.tf_label_data[STAGE][SEQUENTIAL],
            self.tf_label_data[STAGE][SENTENCE],
            seq_mask_label,
            tags_mask,
            self.label_name,
        )
        sentence_tag = self.end_token(tag_transform, seq_lengths_label)

        all_tags_embeded = self._tf_layers[f"embed.{STAGE}"](sentence_tag)

        return all_tag_ids, all_tags_embeded

    def batch_loss(
        self, batch_in: Union[Tuple[tf.Tensor], Tuple[np.ndarray]]
    ) -> tf.Tensor:
        tf_group_data = self.batch_to_model_data_set_format(batch_in, self.data_signature)

        group_dim = self._get_batch_dim(tf_group_data)
        seq_mask_text = super().getting_mask(tf_group_data, TXT, SEQUENCE_LEN)
        seq_lengths_text = self._get_sequence_lengths(
            tf_group_data, TXT, SEQUENCE_LEN, group_dim
        )
        mask_txt = self.computing_mask(seq_lengths_text)

        (
            text_transformed,
            text_in,
            text_seq_ids,
            lm_mask_bool_text,
        ) = self._create_sequence(
            tf_group_data[TXT][SEQUENTIAL],
            tf_group_data[TXT][SENTENCE],
            seq_mask_text,
            mask_txt,
            self.text_name,
            sparse_dropout=self.config[SPARSE_INP_DROP_OUT],
            dense_dropout=self.config[DENSE_INP_DROP_OUT],
            masked_lm_loss=self.config[COVERED_LM],
            sequence_ids=True,
        )

        seq_mask_label = super().getting_mask(
            tf_group_data, STAGE, SEQUENCE_LEN
        )
        seq_lengths_label = self._get_sequence_lengths(
            tf_group_data, STAGE, SEQUENCE_LEN, group_dim
        )
        mask_tags = self.computing_mask(seq_lengths_label)

        tag_transform, _, _, _ = self._create_sequence(
            tf_group_data[STAGE][SEQUENTIAL],
            tf_group_data[STAGE][SENTENCE],
            seq_mask_label,
            mask_tags,
            self.label_name,
        )

        losing = []

        if self.config[COVERED_LM]:
            lossy, account = self._mask_loss(
                text_transformed,
                text_in,
                text_seq_ids,
                lm_mask_bool_text,
                self.text_name,
            )

            self.mask_loss.update_state(lossy)
            self.mask_acc.update_state(account)
            losing.append(lossy)

        # get sentence feature vector for label classification
        sentence_vector_txt = self.end_token(text_transformed, seq_lengths_text)
        sentence_vector_tag = self.end_token(
            tag_transform, seq_lengths_label
        )
        tag_ids = tf_group_data[TAG_KEY][TAG_SUB_KEY][0]

        lossy, account = self._calculate_label_loss(
            sentence_vector_txt, sentence_vector_tag, tag_ids
        )
        self.response_loss.update_state(lossy)
        self.response_acc.update_state(account)
        losing.append(lossy)

        return tf.math.add_n(losing)

    def batch_prediction(
        self, batch_in: Union[Tuple[tf.Tensor], Tuple[np.ndarray]]
    ) -> Dict[Text, tf.Tensor]:
        tf_group_data = self.batch_to_model_data_set_format(
            batch_in, self.predict_data_signature
        )

        seq_mask_text = super().getting_mask(tf_group_data, TXT, SEQUENCE_LEN)
        seq_lengths_text = self._get_sequence_lengths(
            tf_group_data, TXT, SEQUENCE_LEN, batch_dim=1
        )
        txt_mask = self.computing_mask(seq_lengths_text)

        txt_transform, _, _, _ = self._create_sequence(
            tf_group_data[TXT][SEQUENTIAL],
            tf_group_data[TXT][SENTENCE],
            seq_mask_text,
            txt_mask,
            self.text_name,
        )

        outer = {}

        if self.all_labels_embed is None:
            _, self.all_labels_embed = self._make_all_labels()

        # get sentence feature vector for intent classification
        vector_sentence = self.end_token(txt_transform, seq_lengths_text)
        embeded_sentence_vector = self._tf_layers[f"embed.{TXT}"](vector_sentence)

        all_sim = self._tf_layers[f"loss.{STAGE}"].simulation(
            embeded_sentence_vector[:, tf.newaxis, :],
            self.all_labels_embed[tf.newaxis, :, :],
        )
        score = self._tf_layers[f"loss.{STAGE}"].confidence_from_simulation(
            all_sim, self.config[SIMILARITY_TYPE_CATEGORY]
        )
        outer["i_scores"] = score

        return outer
