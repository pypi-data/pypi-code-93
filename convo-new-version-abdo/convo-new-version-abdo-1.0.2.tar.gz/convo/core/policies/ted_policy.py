import copy
import logging
from pathlib import Path
from collections import defaultdict

import numpy as np
import convo.shared.utils.io
import tensorflow as tf
import tensorflow_addons as tfa
import typing
from typing import Any, List, Optional, Text, Dict, Tuple, Union

import convo.utils.io as io_utils
from convo.shared.core.domain import Domain
from convo.core.featurizers.tracker_featurizers import (
    FeaturizerTracker,
    FullDialogueTracerFeaturizer,
    MaxHistoryTrackerFeaturizer,
)
from convo.core.featurizers.single_state_featurizer import SingleStateFeaturizer
from convo.shared.nlu.constants import ACT_TEXT, ACT_NAME, INTENTION, TXT, ENTITIES_NAME
from convo.shared.nlu.interpreter import NaturalLangInterpreter
from convo.core.policies.policy import Policy
from convo.core.constants import BY_DEFAULT_POLICY_PREFERENCE, COMMUNICATION
from convo.shared.core.constants import CURRENT_LOOP   , CONVO_SLOTS
from convo.shared.core.trackers import DialogueStateTracer
from convo.shared.core.generator import TrackerInCachedStates
from convo.utils import train_utils
from convo.utils.tensorflow.models import ConvoModel, ConverterConvoModel
from convo.utils.tensorflow.model_data import ConvoModelDataSet, FeatureSign
from convo.utils.tensorflow.model_data_utils import  conversion_to_data_format
from convo.utils.tensorflow.constants import (
    STAGE,
    TRANSFORMER_DIMENSION,
    NUMBER_TRANSFORMER_LAYERS,
    NUMBER_HEADS,
    BATCH_SIZE,
    GROUP_STRATEGY,
    EPOCHS,
    RAND_SEED,
    LENGTH_RANKING,
    LOSS_CATEGORY,
    SIMILARITY_TYPE_CATEGORY,
    NUMBER_NEG,
    EVALUATE_NUM_EXAMPLES,
    EVALUATE_NUMBER_EPOCHS,
    NEG_MARGIN_SCALE,
    REGULARIZATION_CONST,
    LOSS_SCALE,
    USE_MAXIMUM_NEGATIVE_SIMILARITY,
    MAXIMUM_NEGATIVE_SIMILARITY,
    MAXIMUM_POSITIVE_SIMILARITY,
    EMBEDDING_CAPACITY,
    DROP_RATE_DIALOG,
    LABEL_DROP_RATE,
    DROP_PRICE,
    ATTENTION_DROP_RATE,
    WEIGHT_SPARSE,
    RELATIVE_ATTENTION_KEY,
    RELATIVE_ATTENTION_VAL,
    RELATIVE_POSITION_MAXIMUM,
    SOFT_MAX,
    AUTOMATIC,
    BALANCED_VALUE,
    TENSOR_BOARD_LOG_DIRECTORY,
    TENSOR_BOARD_LOGGING_LEVEL,
    CHECK_POINT_MODEL,
    ENCODING_CAPACITY,
    UNI_DIRECTIONAL_ENCODER,
    SEQUENTIAL,
    SENTENCE,
    DIMENSION_DENSE,
)


if typing.TYPE_CHECKING:
    from convo.shared.nlu.training_data.features import Features


log = logging.getLogger(__name__)

COVER = "mask"
LABEL_KEY_NAME = STAGE
LABEL_SUB_KEY_NAME = "ids"
LEN = "length"
POSSIBLE_FEATURE_TYPE = [SEQUENTIAL, SENTENCE]
FEATURES_TO_ENCRYPT = [INTENTION, TXT, ACT_NAME, ACT_TEXT]
LABEL_FEATURES_TO_ENCODE_ENCRYPT = [f"{STAGE}_{ACT_NAME}", f"{STAGE}_{ACT_TEXT}"]
STATE_LEVEL_FEATURE = [ENTITIES_NAME, CONVO_SLOTS, CURRENT_LOOP]

SAVE_MODEL_FILENAME = "ted_policy"


class TEDPolicy(Policy):
    """Transformer Embedding Dialogue (TED) Policy is described in
    https://arxiv.org/abs/1910.00486.
    This policy has a pre-defined architecture, which comprises the
    following steps:
        - concatenate user input (user intent and entities), previous system actions,
          convo_slotsand active forms for each time step into an input vector to
          pre-transformer embedding layer;
        - feed it to transformer;
        - apply a dense layer to the output of the transformer to get embeddings of a
          dialogue for each time step;
        - apply a dense layer to create embeddings for system actions for each time
          step;
        - calculate the similarity between the dialogue embedding and embedded system
          actions. This step is based on the StarSpace
          (https://arxiv.org/abs/1709.03856) idea.
    """

    # please make sure to update the docs when changing a default parameter
    defaults = {
        # ## Architecture of the used neural network
        # Hidden layer sizes for layers before the dialogue and label embedding layers.
        # The number of hidden layers is equal to the length of the corresponding
        # list.
        # TODO add 2 parallel NNs: transformer for text and ffnn for names
        DIMENSION_DENSE: 20,
        ENCODING_CAPACITY: 50,
        # Number of units in transformer
        TRANSFORMER_DIMENSION: 128,
        # Number of transformer layers
        NUMBER_TRANSFORMER_LAYERS: 1,
        # Number of attention heads in transformer
        NUMBER_HEADS: 4,
        # If 'True' use key relative embeddings in attention
        RELATIVE_ATTENTION_KEY: False,
        # If 'True' use value relative embeddings in attention
        RELATIVE_ATTENTION_VAL: False,
        # Max position for relative embeddings
        RELATIVE_POSITION_MAXIMUM: None,
        # Use a unidirectional or bidirectional encoder.
        UNI_DIRECTIONAL_ENCODER: True,
        # ## Training parameters
        # Initial and final batch sizes:
        # Batch size will be linearly increased for each epoch.
        BATCH_SIZE: [64, 256],
        # Strategy used whenc creating batches.
        # Can be either 'sequence' or 'balanced'.
        GROUP_STRATEGY: BALANCED_VALUE,
        # Number of epochs to train
        EPOCHS: 1,
        # Set random seed to any 'int' to get reproducible results
        RAND_SEED: None,
        # ## Parameters for embeddings
        # Dimension size of embedding vectors
        EMBEDDING_CAPACITY: 20,
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
        MAXIMUM_NEGATIVE_SIMILARITY: -0.2,
        # If 'True' the algorithm only minimizes maximum similarity over
        # incorrect intent labels, used only if 'loss_type' is set to 'margin'.
        USE_MAXIMUM_NEGATIVE_SIMILARITY: True,
        # If 'True' scale loss inverse proportionally to the confidence
        # of the correct prediction
        LOSS_SCALE: True,
        # ## Regularization parameters
        # The scale of regularization
        REGULARIZATION_CONST: 0.001,
        # The scale of how important is to minimize the maximum similarity
        # between embeddings of different labels,
        # used only if 'loss_type' is set to 'margin'.
        NEG_MARGIN_SCALE: 0.8,
        # Dropout rate for embedding layers of dialogue features.
        DROP_RATE_DIALOG: 0.1,
        # Dropout rate for embedding layers of utterance level features.
        DROP_PRICE: 0.0,
        # Dropout rate for embedding layers of label, e.g. action, features.
        LABEL_DROP_RATE: 0.0,
        # Dropout rate for attention.
        ATTENTION_DROP_RATE: 0,
        # Sparsity of the weights in dense layers
        WEIGHT_SPARSE: 0.8,
        # ## Evaluation parameters
        # How often calculate validation accuracy.
        # Small values may hurt performance, e.g. model accuracy.
        EVALUATE_NUMBER_EPOCHS: 20,
        # How many examples to use for hold out validation set
        # Large values may hurt performance, e.g. model accuracy.
        EVALUATE_NUM_EXAMPLES: 0,
        # If you want to use tensorboard to visualize training and validation metrics,
        # set this option to a valid output dir.
        TENSOR_BOARD_LOG_DIRECTORY: None,
        # Define when training metrics for tensorboard should be logged.
        # Either after every epoch or for every training step.
        # Valid values: 'epoch' and 'minibatch'
        TENSOR_BOARD_LOGGING_LEVEL: "epoch",
        # Perform model checkpointing
        CHECK_POINT_MODEL: False,
    }

    @staticmethod
    def _standard_featurizer(max_history: Optional[int] = None) -> FeaturizerTracker:
        return MaxHistoryTrackerFeaturizer(
            SingleStateFeaturizer(), max_history=max_history
        )

    def __init__(
        self,
        featurizer: Optional[FeaturizerTracker] = None,
        priority: int = BY_DEFAULT_POLICY_PREFERENCE,
        max_history: Optional[int] = None,
        model: Optional[ConvoModel] = None,
        zero_state_features: Optional[Dict[Text, List["Features"]]] = None,
        **kwargs: Any,
    ) -> None:
        """Declare instance variables with default values."""

        if not featurizer:
            featurizer = self._standard_featurizer(max_history)

        super().__init__(featurizer, priority)
        if isinstance(featurizer, FullDialogueTracerFeaturizer):
            self.is_full_dialogue_featurizer_used = True
        else:
            self.is_full_dialogue_featurizer_used = False

        self._load_parameters(**kwargs)

        self.model = model

        self.zero_state_features = zero_state_features or defaultdict(list)

        self._label_data: Optional[ConvoModelDataSet] = None
        self.data_example: Optional[Dict[Text, List[np.ndarray]]] = None

    def _load_parameters(self, **kwargs: Dict[Text, Any]) -> None:
        self.config = copy.deepcopy(self.defaults)
        self.config.update(kwargs)

        self.config = train_utils.validating_deprecated_options(self.config)

        self.config = train_utils.updating_similarity_type(self.config)
        self.config = train_utils.updating_evaluation_params(self.config)

    def _generate_label_data(
        self, domain: Domain, interpreter: NaturalLangInterpreter
    ) -> Tuple[ConvoModelDataSet, List[Dict[Text, List["Features"]]]]:
        # encode all label_ids with policies' featurizer
        state_featurizer = self.featurizer.state_featurizer
        encrypted_all_labels = state_featurizer.encode_all_acts(domain, interpreter)

        attribute_data_set, _ =  conversion_to_data_format(encrypted_all_labels)

        label_data_set = ConvoModelDataSet()
        label_data_set.adding_new_data(attribute_data_set, key_prefix=f"{LABEL_KEY_NAME}_")

        label_id = np.arange(domain.number_of_actions)
        label_data_set.adding_features(
            LABEL_KEY_NAME, LABEL_SUB_KEY_NAME, [np.expand_dims(label_id, -1)]
        )

        return label_data_set, encrypted_all_labels

    def _generate_model_data(
        self,
        tracker_state_features: List[List[Dict[Text, List["Features"]]]],
        label_id: Optional[np.ndarray] = None,
        encoded_all_labels: Optional[List[Dict[Text, List["Features"]]]] = None,
    ) -> ConvoModelDataSet:
        """Combine all model related data into ConvoModelDataSet.

        Args:
            tracker_state_features: a dictionary of attributes (INTENTION, TXT, ACT_NAME, ACT_TEXT,
                ENTITIES_NAME, CONVO_SLOTS, CURRENT_LOOP   ) to a list of features for all dialogue
                turns in all training trackers
            label_id: the label ids (e.g. action ids) for every dialogue turn in all
                training trackers
            encoded_all_labels: a list of dictionaries containing attribute features for labels ids

        Returns:
            ConvoModelDataSet
        """
        model_data_set = ConvoModelDataSet(label_key=LABEL_KEY_NAME, label_sub_key=LABEL_SUB_KEY_NAME)

        if label_id is not None and encoded_all_labels is not None:

            label_id = np.array(
                [np.expand_dims(seq_label_ids, -1) for seq_label_ids in label_id]
            )
            model_data_set.adding_features(LABEL_KEY_NAME, LABEL_SUB_KEY_NAME, [label_id])

            attribute_data_set, self.zero_state_features =  conversion_to_data_format(
                tracker_state_features
            )
        else:
            # method is called during prediction
            attribute_data_set, _ =  conversion_to_data_format(
                tracker_state_features, self.zero_state_features
            )

        model_data_set.adding_new_data(attribute_data_set)
        model_data_set.adding_len(
            COMMUNICATION, LEN, next(iter(list(attribute_data_set.keys()))), COVER
        )

        return model_data_set

    def train(
        self,
        training_trackers: List[TrackerInCachedStates],
        domain: Domain,
        interpreter: NaturalLangInterpreter,
        **kwargs: Any,
    ) -> None:
        """Train the policy on given training trackers."""

        if not training_trackers:
            log.error(
                f"Can not train '{self.__class__.__name__}'. No data was provided. "
                f"Skipping training of the policy."
            )
            return

        # dealing with training data
        tracker_state_features, label_id = self.featurize_for_training(
            training_trackers, domain, interpreter, **kwargs
        )

        self._label_data, encoded_all_labels = self._generate_label_data(
            domain, interpreter
        )

        # extract actual training data to feed to model
        model_data_set = self._generate_model_data(
            tracker_state_features, label_id, encoded_all_labels
        )
        if model_data_set.empty_check():
            log.error(
                f"Can not train '{self.__class__.__name__}'. No data was provided. "
                f"Skipping training of the policy."
            )
            return

        # keep one example for persisting and loading
        self.data_example = model_data_set.first_data_exp()

        self.model = TED(
            model_data_set.get_sign(),
            self.config,
            isinstance(self.featurizer, MaxHistoryTrackerFeaturizer),
            self._label_data,
        )

        self.model.fit(
            model_data_set,
            self.config[EPOCHS],
            self.config[BATCH_SIZE],
            self.config[EVALUATE_NUM_EXAMPLES],
            self.config[EVALUATE_NUMBER_EPOCHS],
            batch_strategy=self.config[GROUP_STRATEGY],
        )

    def predict_action_probabilities(
        self,
        tracker: DialogueStateTracer,
        domain: Domain,
        interpreter: NaturalLangInterpreter,
        **kwargs: Any,
    ) -> List[float]:
        """Predict the next action the bot should take.
        Return the list of probabilities for the next actions.
        """

        if self.model is None:
            return self._default_predictions(domain)

        # create model data from tracker
        tracker_state_features = self.featurizer.create_state_features(
            [tracker], domain, interpreter
        )
        model_data_set = self._generate_model_data(tracker_state_features)

        result = self.model.predict(model_data_set)

        confidence = result["action_scores"].numpy()
        # remove batch dimension and take the last prediction in the sequence
        confidence = confidence[0, -1, :]

        if self.config[LOSS_CATEGORY] == SOFT_MAX and self.config[LENGTH_RANKING] > 0:
            confidence = train_utils.normalization(confidence, self.config[LENGTH_RANKING])

        return confidence.tolist()

    def persist(self, path: Union[Text, Path]) -> None:
        """Persists the policy to a storage."""

        if self.model is None:
            log.debug(        """Train the policy on given training trackers."""

                "Method `persist(...)` was called "
                "without a trained model present. "
                "Nothing to persist then!"
            )
            return

        model_path_flow = Path(path)
        tf_model_file_name = model_path_flow / f"{SAVE_MODEL_FILENAME}.tf_model"

        convo.shared.utils.io.create_dir_from_file(tf_model_file_name)

        self.featurizer.persist(path)

        if self.model.checkpoint_model:
            self.model.copying_best(str(tf_model_file_name))
        else:
            self.model.save(str(tf_model_file_name))

        io_utils.dictionary_pickle(
            model_path_flow / f"{SAVE_MODEL_FILENAME}.priority.pkl", self.priority
        )
        io_utils.pick_data(
            model_path_flow / f"{SAVE_MODEL_FILENAME}.meta.pkl", self.config
        )
        io_utils.pick_data(
            model_path_flow / f"{SAVE_MODEL_FILENAME}.data_example.pkl", self.data_example
        )
        io_utils.pick_data(
            model_path_flow / f"{SAVE_MODEL_FILENAME}.zero_state_features.pkl",
            self.zero_state_features,
        )
        io_utils.pick_data(
            model_path_flow / f"{SAVE_MODEL_FILENAME}.label_data.pkl",
            dict(self._label_data.data),
        )

    @classmethod
    def load(cls, path: Union[Text, Path]) -> "TEDPolicy":
        """Loads a policy from the storage.
        **Needs to load its featurizer**
        """
        model_path_flow = Path(path)

        if not model_path_flow.exists():
            raise Exception(
                f"Failed to load TED policy model. Path "
                f"'{model_path_flow.absolute()}' doesn't exist."
            )

        tf_model_file_name = model_path_flow / f"{SAVE_MODEL_FILENAME}.tf_model"

        feature = FeaturizerTracker.load(path)

        if not (model_path_flow / f"{SAVE_MODEL_FILENAME}.data_example.pkl").is_file():
            return cls(featurizer=feature)

        loaded_data_set = io_utils.pick_load(
            model_path_flow / f"{SAVE_MODEL_FILENAME}.data_example.pkl"
        )
        label_data_set = io_utils.pick_load(
            model_path_flow / f"{SAVE_MODEL_FILENAME}.label_data.pkl"
        )
        features_with_zero_state = io_utils.pick_load(
            model_path_flow / f"{SAVE_MODEL_FILENAME}.zero_state_features.pkl"
        )
        label_data_set = ConvoModelDataSet(data=label_data_set)
        meta_data = io_utils.pick_load(model_path_flow / f"{SAVE_MODEL_FILENAME}.meta.pkl")
        preference = io_utils.json_un_pickle(
            model_path_flow / f"{SAVE_MODEL_FILENAME}.priority.pkl"
        )

        model_data_eg = ConvoModelDataSet(
            label_key=LABEL_KEY_NAME, label_sub_key=LABEL_SUB_KEY_NAME, data=loaded_data_set
        )
        meta_data = train_utils.updating_similarity_type(meta_data)

        model = TED.load(
            str(tf_model_file_name),
            model_data_eg,
            data_signature=model_data_eg.get_sign(),
            config=meta_data,
            max_history_tracker_featurizer_used=isinstance(
                feature, MaxHistoryTrackerFeaturizer
            ),
            label_data=label_data_set,
        )

        # build the graph for prediction
        forecast_data_set_example = ConvoModelDataSet(
            label_key=LABEL_KEY_NAME,
            label_sub_key=LABEL_SUB_KEY_NAME,
            data={
                feature_name: features
                for feature_name, features in model_data_eg.items()
                if feature_name
                   in STATE_LEVEL_FEATURE + FEATURES_TO_ENCRYPT + [COMMUNICATION]
            },
        )
        model.build_for_prediction(forecast_data_set_example)

        return cls(
            featurizer=feature,
            priority=preference,
            model=model,
            zero_state_features=features_with_zero_state,
            **meta_data,
        )


# accessing _tf_layers with any key results in key-error, disable it
# pytype: disable=key-error


class TED(ConverterConvoModel):
    def __init__(
        self,
        data_signature: Dict[Text, Dict[Text, List[FeatureSign]]],
        config: Dict[Text, Any],
        max_history_tracker_featurizer_used: bool,
        label_data: ConvoModelDataSet,
    ) -> None:
        super().__init__("TED", config, data_signature, label_data)

        self.max_history_tracker_featurizer_used = max_history_tracker_featurizer_used

        self.predict_data_signature = {
            feature_name: features
            for feature_name, features in data_signature.items()
            if feature_name in STATE_LEVEL_FEATURE + FEATURES_TO_ENCRYPT + [COMMUNICATION]
        }

        # optimizer
        self.optimizer = tf.keras.optimizers.Adam()

        # metrics
        self.action_loss = tf.keras.metrics.Mean(name="loss")
        self.action_acc = tf.keras.metrics.Mean(name="acc")
        self.metrics_to_log += ["loss", "acc"]

        self.all_labels_embed = None  # needed for efficient prediction

        self._prepare_layers()

    def _check_data(self) -> None:
        if not any(key in [INTENTION, TXT] for key in self.data_signature.keys()):
            raise ValueError(
                f"No user features specified. "
                f"Cannot train '{self.__class__.__name__}' model."
            )

        if not any(
            key in [ACT_NAME, ACT_TEXT] for key in self.data_signature.keys()
        ):
            raise ValueError(
                f"No action features specified. "
                f"Cannot train '{self.__class__.__name__}' model."
            )
        if STAGE not in self.data_signature:
            raise ValueError(
                f"No label features specified. "
                f"Cannot train '{self.__class__.__name__}' model."
            )

    def _prepare_layers(self) -> None:
        for name in self.data_signature.keys():
            self._produce_sparse_dense_layer_for(name, self.data_signature)
            self._produce_encoding_layers(name)

        for name in self.label_signature.keys():
            self._produce_sparse_dense_layer_for(name, self.label_signature)
            self._produce_encoding_layers(name)

        self.transformer_layer_preparation(
            COMMUNICATION, self.config[DROP_RATE_DIALOG], self.config[ATTENTION_DROP_RATE]
        )

        self.preparing_embedding_layers(COMMUNICATION)
        self.preparing_embedding_layers(STAGE)

        self.dot_product_loss_preparation(STAGE, self.config[LOSS_SCALE])

    def _produce_sparse_dense_layer_for(
        self, name: Text, signature: Dict[Text, Dict[Text, List[FeatureSign]]]
    ) -> None:
        """Prepare the sparse dense layer for the given attribute name. It is used to
        combine the sparse and dense features of the attribute at the beginning of
        the model.

        Args:
            name: the attribute name
            signature: data signature
        """
        for feature_type in POSSIBLE_FEATURE_TYPE:
            if name not in signature or feature_type not in signature[name]:
                # features for feature type are not present
                continue

            self.sparse_dense_dropout_layers_preparation(
                f"{name}_{feature_type}", self.config[DROP_PRICE]
            )

            # use the same configurable dense dimension for all sparse features
            self.sparse_dense_layers_preparation(
                signature[name][feature_type],
                f"{name}_{feature_type}",
                self.config[DIMENSION_DENSE],
            )

    def _produce_encoding_layers(self, name: Text) -> None:
        """Create ffnn layer for given attribute name. The layer is used just before
        all dialogue features are combined.

        Args:
            name: attribute name
        """
        feature_variety = SENTENCE
        # create encoding layers only for the features which should be encoded;
        if name not in FEATURES_TO_ENCRYPT + LABEL_FEATURES_TO_ENCODE_ENCRYPT:
            return
        # check that there are SENTENCE features for the attribute name in data
        if name in FEATURES_TO_ENCRYPT and feature_variety not in self.data_signature[name]:
            return
        #  same for label_data
        if (
            name in LABEL_FEATURES_TO_ENCODE_ENCRYPT
            and feature_variety not in self.label_signature[name]
        ):
            return

        self.ffnn_layer_preparation(
            f"{name}_{feature_variety}",
            [self.config[ENCODING_CAPACITY]],
            self.config[DROP_RATE_DIALOG],
        )

    def _generate_all_labels_embed(self) -> Tuple[tf.Tensor, tf.Tensor]:
        all_label_ids = self.tf_label_data[LABEL_KEY_NAME][LABEL_SUB_KEY_NAME][0]
         
        all_labels_encoded = {
            key: self._encode_features_per_attri(self.tf_label_data, key)
            for key in self.tf_label_data.keys()
            if key != LABEL_KEY_NAME
        }

        if (
            all_labels_encoded.get(f"{LABEL_KEY_NAME}_{ACT_TEXT}") is not None
            and all_labels_encoded.get(f"{LABEL_KEY_NAME}_{ACT_NAME}") is not None
        ):
            y = all_labels_encoded.pop(
                f"{LABEL_KEY_NAME}_{ACT_TEXT}"
            ) + all_labels_encoded.pop(f"{LABEL_KEY_NAME}_{ACT_NAME}")
        elif all_labels_encoded.get(f"{LABEL_KEY_NAME}_{ACT_TEXT}") is not None:
            y = all_labels_encoded.pop(f"{LABEL_KEY_NAME}_{ACT_TEXT}")
        else:
            y = all_labels_encoded.pop(f"{LABEL_KEY_NAME}_{ACT_NAME}")

        # additional sequence axis is artifact of our ConvoModelDataSet creation
        # TODO check whether this should be solved in data creation
        y = tf.squeeze(y, axis=1)

        all_labels_combination = self._tf_layers[f"embed.{STAGE}"](y)

        return all_label_ids, all_labels_combination

    def _emebeding_dialogue(
        self, dialogue_in: tf.Tensor, sequence_lengths: tf.Tensor
    ) -> Tuple[tf.Tensor, tf.Tensor]:
        """Create dialogue level embedding and mask."""

        get_mask = self.computing_mask(sequence_lengths)

        dialogue_modified = self._tf_layers[f"transformer.{COMMUNICATION}"](
            dialogue_in, 1 - get_mask, self._training
        )
        dialogue_modified = tfa.activations.gelu(dialogue_modified)

        if self.max_history_tracker_featurizer_used:
            # pick last vector if max history featurizer is used
            dialogue_modified = tf.expand_dims(
                self.end_token(dialogue_modified, sequence_lengths), 1
            )
            get_mask = tf.expand_dims(self.end_token(get_mask, sequence_lengths), 1)

        dialogue_combined = self._tf_layers[f"embed.{COMMUNICATION}"](dialogue_modified)

        return dialogue_combined, get_mask

    def _encode_features_per_attri(
        self, tf_batch_data: Dict[Text, Dict[Text, List[tf.Tensor]]], attribute: Text
    ) -> Optional[tf.Tensor]:
        """
        Encodes features for a given attribute
        Args:
            tf_batch_data: dictionary mapping every attribute to its features and masks
            attribute: the attribute we will encode features for (e.g., ACT_NAME, INTENTION)
        Returns:
            A tensor combining  all features for `attribute`
        """

        if not tf_batch_data[attribute]:
            return None

        attr_mask = tf_batch_data[attribute][COVER][0]
        # TODO transformer has to be used to process sequence features
        attr_features = self._combine_sparse_dense_features(
            tf_batch_data[attribute][SENTENCE],
            f"{attribute}_{SENTENCE}",
            mask=attr_mask,
        )

        if attribute in FEATURES_TO_ENCRYPT + LABEL_FEATURES_TO_ENCODE_ENCRYPT:
            attr_features = self._tf_layers[f"ffnn.{attribute}_{SENTENCE}"](
                attr_features
            )
        return attr_features * attr_mask

    def _process_batch_data_set(
        self, tf_batch_data: Dict[Text, Dict[Text, List[tf.Tensor]]]
    ) -> tf.Tensor:
        """Encodes batch data; combines intent and text and action name and action text if both are present
        Args:
            tf_batch_data: dictionary mapping every attribute to its features and masks
        Returns:
             Tensor: encoding of all features in the batch, combined;
        """
        # encode each attribute present in tf_batch_data
        batch_encrypted = {
            key: self._encode_features_per_attri(tf_batch_data, key)
            for key in tf_batch_data.keys()
            if LABEL_KEY_NAME not in key and COMMUNICATION not in key
        }
        # if both action text and action name are present, combine them; otherwise, return the one which is present

        if (
            batch_encrypted.get(ACT_TEXT) is not None
            and batch_encrypted.get(ACT_NAME) is not None
        ):
            batch_act = batch_encrypted.pop(ACT_TEXT) + batch_encrypted.pop(
                ACT_NAME
            )
        elif batch_encrypted.get(ACT_TEXT) is not None:
            batch_act = batch_encrypted.pop(ACT_TEXT)
        else:
            batch_act = batch_encrypted.pop(ACT_NAME)
        # same for user input
        if (
            batch_encrypted.get(INTENTION) is not None
            and batch_encrypted.get(TXT) is not None
        ):
            user_batches = batch_encrypted.pop(INTENTION) + batch_encrypted.pop(TXT)
        elif batch_encrypted.get(TXT) is not None:
            user_batches = batch_encrypted.pop(TXT)
        else:
            user_batches = batch_encrypted.pop(INTENTION)

        batch_features = [user_batches, batch_act]
        # once we have user input and previous action,
        # add all others attributes (CONVO_SLOTS, CURRENT_LOOP   , etc.) to batch_features;
        for key in batch_encrypted.keys():
            batch_features.append(batch_encrypted.get(key))

        batch_features = tf.concat(batch_features, axis=-1)

        return batch_features

    @staticmethod
    def  _fetch_labels_embed(
        label_ids: tf.Tensor, all_labels_embed: tf.Tensor
    ) -> tf.Tensor:
        # instead of processing labels again, gather embeddings from
        # all_labels_embed using label ids

        indexes = tf.cast(label_ids[:, :, 0], tf.int32)
        labels_combined = tf.gather(all_labels_embed, indexes)

        return labels_combined

    def batch_loss(
        self, batch_in: Union[Tuple[tf.Tensor], Tuple[np.ndarray]]
    ) -> tf.Tensor:
        tf_batch_data_set = self.batch_to_model_data_set_format(batch_in, self.data_signature)

        dialogue_len = tf.cast(tf_batch_data_set[COMMUNICATION][LEN][0], tf.int32)

        all_label_id, all_labels_combined = self._generate_all_labels_embed()

        label_id = tf_batch_data_set[LABEL_KEY_NAME][LABEL_SUB_KEY_NAME][0]
        labels_combined = self._fetch_labels_embed(label_id, all_labels_combined)

        dialogue = self._process_batch_data_set(tf_batch_data_set)
        dialogue_combined, masked_dialogue = self._emebeding_dialogue(
            dialogue, dialogue_len
        )
        masked_dialogue = tf.squeeze(masked_dialogue, axis=-1)

        get_loss, account = self._tf_layers[f"loss.{STAGE}"](
            dialogue_combined,
            labels_combined,
            label_id,
            all_labels_combined,
            all_label_id,
            masked_dialogue,
        )

        self.action_loss.update_state(get_loss)
        self.action_acc.update_state(account)

        return get_loss

    def batch_predict(
        self, batch_in: Union[Tuple[tf.Tensor], Tuple[np.ndarray]]
    ) -> Dict[Text, tf.Tensor]:
        tf_batch_data_set = self.batch_to_model_data_set_format(
            batch_in, self.predict_data_signature
        )

        dialogue_len = tf.cast(tf_batch_data_set[COMMUNICATION][LEN][0], tf.int32)

        if self.all_labels_embed is None:
            _, self.all_labels_embed = self._generate_all_labels_embed()

        dialogue = self._process_batch_data_set(tf_batch_data_set)
        dialogue_combined, mask_dialogue = self._emebeding_dialogue(
            dialogue, dialogue_len
        )
        mask_dialogue = tf.squeeze(mask_dialogue, axis=-1)

        each_sim = self._tf_layers[f"loss.{STAGE}"].simulation(
            dialogue_combined[:, :, tf.newaxis, :],
            self.all_labels_embed[tf.newaxis, tf.newaxis, :, :],
            mask_dialogue,
        )

        score_card = self._tf_layers[f"loss.{STAGE}"].confidence_from_simulation(
            each_sim, self.config[SIMILARITY_TYPE_CATEGORY]
        )

        return {"action_scores": score_card}


# pytype: enable=key-error
