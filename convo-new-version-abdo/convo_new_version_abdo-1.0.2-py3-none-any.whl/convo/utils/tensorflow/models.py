import datetime

import tensorflow as tf
import numpy as np
import logging
import os
import shutil
from collections import defaultdict
from pathlib import Path
from typing import (
    List,
    Text,
    Dict,
    Tuple,
    Union,
    Optional,
    Callable,
    TYPE_CHECKING,
    Any,
)

from tqdm import tqdm
from convo.constants import CHECKS_FOR_MODEL_NAME
from convo.shared.utils.io import logging_disabled_check
import convo.utils.io
from convo.utils.tensorflow.model_data import ConvoModelDataSet, FeatureSign
from convo.utils.tensorflow.constants import (
    SEQUENTIAL,
    TENSOR_BOARD_LOGGING_LEVEL,
    RAND_SEED,
    TENSOR_BOARD_LOG_DIRECTORY,
    CHECK_POINT_MODEL,
    EMBEDDING_CAPACITY,
    REGULARIZATION_CONST,
    SIMILARITY_TYPE_CATEGORY,
    WEIGHT_SPARSE,
    NUMBER_TRANSFORMER_LAYERS,
    TRANSFORMER_DIMENSION,
    NUMBER_HEADS,
    UNI_DIRECTIONAL_ENCODER,
    RELATIVE_ATTENTION_KEY,
    RELATIVE_ATTENTION_VAL,
    RELATIVE_POSITION_MAXIMUM,
    NUMBER_NEG,
    LOSS_CATEGORY,
    MAXIMUM_POSITIVE_SIMILARITY,
    MAXIMUM_NEGATIVE_SIMILARITY,
    USE_MAXIMUM_NEGATIVE_SIMILARITY,
    NEG_MARGIN_SCALE,
)
from convo.utils.tensorflow import layers
from convo.utils.tensorflow.transformer import ConverterEncoder

if TYPE_CHECKING:
    from tensorflow.python.ops.summary_ops_v2 import ResourceSummaryWriter

logger = logging.getLogger(__name__)


TENSOR_BOARD_LOGGING_LEVELS = ["epoch", "minibatch"]


# noinspection PyMethodOverriding
class ConvoModel(tf.keras.models.Model):
    """Completely override all public methods of keras Model.

    Cannot be used as tf.keras.Model
    """


    def __init__(
        self,
        random_seed: Optional[int] = None,
        tensorboard_log_dir: Optional[Text] = None,
        tensorboard_log_level: Optional[Text] = "epoch",
        checkpoint_model: Optional[bool] = False,
        **kwargs,
    ) -> None:
        """Initialize the ConvoModel.

        Args:
            random_seed: set the random seed to get reproducible results
        """
        super().__init__(**kwargs)

        self.total_loss = tf.keras.metrics.Mean(name="t_loss")
        self.metrics_to_log = ["t_loss"]

        self._training = None  # training phase should be defined when building a graph

        self._predict_function = None

        self.random_seed = random_seed

        self.tensorboard_log_dir = tensorboard_log_dir
        self.tensorboard_log_level = tensorboard_log_level

        self.train_summary_writer = None
        self.test_summary_writer = None
        self.model_summary_file = None
        self.tensorboard_log_on_epochs = True

        self.best_metrics_so_far = {}
        self.checkpoint_model = checkpoint_model
        self.best_model_file = None
        self.best_model_epoch = -1
        if self.checkpoint_model:
            model_checkpoint_dir = convo.utils.io.create_temp_dir()
            self.best_model_file = os.path.join(
                model_checkpoint_dir, f"{CHECKS_FOR_MODEL_NAME}.tf_model"
            )

    def setting_up_tensor_board_writer(self) -> None:
        if self.tensorboard_log_dir is not None:
            if self.tensorboard_log_level not in TENSOR_BOARD_LOGGING_LEVELS:
                raise ValueError(
                    f"Provided '{TENSOR_BOARD_LOGGING_LEVEL}' ('{self.tensorboard_log_level}') "
                    f"is invalid! Valid values are: {TENSOR_BOARD_LOGGING_LEVELS}"
                )
            self.tensorboard_log_on_epochs = self.tensorboard_log_level == "epoch"

            curr_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            classname = self.__class__.__name__

            train_log_directory = (
                f"{self.tensorboard_log_dir}/{classname}/{curr_time}/train"
            )
            test_log_directory = (
                f"{self.tensorboard_log_dir}/{classname}/{curr_time}/test"
            )

            self.train_summary_writer = tf.summary.create_file_writer(train_log_directory)
            self.test_summary_writer = tf.summary.create_file_writer(test_log_directory)

            self.model_summary_file = f"{self.tensorboard_log_dir}/{classname}/{curr_time}/model_summary.txt"

    def batch_loss(
        self, batch_in: Union[Tuple[tf.Tensor], Tuple[np.ndarray]]
    ) -> tf.Tensor:
        raise NotImplementedError

    def batch_predict(
        self, batch_in: Union[Tuple[tf.Tensor], Tuple[np.ndarray]]
    ) -> Dict[Text, tf.Tensor]:
        raise NotImplementedError

    def fit(
        self,
        model_data_set: ConvoModelDataSet,
        epochs: int,
        batch_size: Union[List[int], int],
        evaluate_on_num_examples: int,
        evaluate_every_num_epochs: int,
        batch_strategy: Text,
        silent: bool = False,
        loading: bool = False,
        eager: bool = False,
    ) -> None:
        """Fit model data"""

        # don't setup tensorboard writers when training during loading
        if not loading:
            self.setting_up_tensor_board_writer()

        tf.random.set_seed(self.random_seed)
        np.random.seed(self.random_seed)

        disabled = silent or logging_disabled_check()

        evaluate_model_data_set = None
        if evaluate_on_num_examples > 0:
            if not disabled:
                logger.info(
                    f"Validation accuracy is calculated every "
                    f"{evaluate_every_num_epochs} epochs."
                )

            model_data_set, evaluate_model_data_set = model_data_set.split(
                evaluate_on_num_examples, self.random_seed
            )

        (
            train_dataset_function,
            tf_train_on_batch_function,
        ) = self.get_tf_train_funcs(eager, model_data_set, batch_strategy)
        (
            evaluation_dataset_function,
            tf_evaluation_on_batch_function,
        ) = self.get_tf_evaluation_func(eager, evaluate_model_data_set)

        evaluation_results = {}  # validation is not performed every epoch
        prog_bar = tqdm(range(epochs), desc="Epochs", disable=disabled)

        steps_for_training = 0

        for epoch in prog_bar:
            batch_size_epoch = self.increasing_batch_size_linearly(
                epoch, batch_size, epochs
            )

            steps_for_training = self.batch_loop(
                train_dataset_function,
                tf_train_on_batch_function,
                batch_size_epoch,
                True,
                steps_for_training,
                self.train_summary_writer,
            )

            if self.tensorboard_log_on_epochs:
                self.log_metrics_for_tensor_board(epoch, self.train_summary_writer)

            post_fix_dictionary = self.get_metric_res()

            if evaluate_on_num_examples > 0:
                if self.should_eval(evaluate_every_num_epochs, epochs, epoch):
                    self.batch_loop(
                        evaluation_dataset_function,
                        tf_evaluation_on_batch_function,
                        batch_size_epoch,
                        False,
                        steps_for_training,
                        self.test_summary_writer,
                    )

                    if self.tensorboard_log_on_epochs:
                        self.log_metrics_for_tensor_board(
                            epoch, self.test_summary_writer
                        )

                    evaluation_results = self.get_metric_res(affix="val_")
                    self.save_model_check_point(
                        current_results=evaluation_results, epoch=epoch
                    )

                post_fix_dictionary.update(evaluation_results)

            prog_bar.set_postfix(post_fix_dictionary)

        if self.checkpoint_model:
            logger.info(
                f"The model of epoch {self.best_model_epoch} (out of {epochs} in total) will be stored!"
            )
        if self.model_summary_file is not None:
            self.writing_model_summary()

        self._training = None  # training phase should be defined when building a graph
        if not disabled:
            logger.info("Finished training.")

    def batch_training(
        self, batch_in: Union[Tuple[tf.Tensor], Tuple[np.ndarray]]
    ) -> None:
        """Train on batch"""

        # calculate supervision and regularization losses separately
        with tf.GradientTape(persistent=True) as tape:
            predict_loss = self.batch_loss(batch_in)
            loss_regularizarion = tf.math.add_n(self.losses)
            loss_total = predict_loss + loss_regularizarion

        self.total_loss.update_state(loss_total)

        # calculate the gradients that come from supervision signal
        predict_gradients = tape.gradient(predict_loss, self.trainable_variables)
        # calculate the gradients that come from regularization
        regularize_gradients = tape.gradient(
            loss_regularizarion, self.trainable_variables
        )
        # delete gradient tape manually
        # since it was created with `persistent=True` option
        del tape

        rise = []
        for pred_grad, reg_grad in zip(predict_gradients, regularize_gradients):
            if pred_grad is not None and reg_grad is not None:
                # remove regularization gradient for variables
                # that don't have prediction gradient
                rise.append(
                    pred_grad
                    + tf.where(pred_grad > 0, reg_grad, tf.zeros_like(reg_grad))
                )
            else:
                rise.append(pred_grad)

        self.optimizer.apply_gradients(zip(rise, self.trainable_variables))

    def build_for_prediction(
        self, predict_data: ConvoModelDataSet, eager: bool = False
    ) -> None:
        self._training = False  # needed for tf graph mode
        self._predict_function = self.get_tf_call_model_func(
            predict_data.as_tf_data_set, self.batch_predict, eager, "prediction"
        )

    def predict(self, predict_data: ConvoModelDataSet) -> Dict[Text, tf.Tensor]:
        if self._predict_function is None:
            logger.debug("There is no tensorflow prediction graph.")
            self.build_for_prediction(predict_data)

        # Prepare a single batch of size 1
        group_in = predict_data.preparing_batch_data(start=0, end=1)

        self._training = False  # needed for eager mode
        return self._predict_function(group_in)

    def save(self, model_file_name: Text, overwrite: bool = True) -> None:
        self.save_weights(model_file_name, overwrite=overwrite, save_format="tf")

    def copying_best(self, model_file_name: Text) -> None:
        check_point_dir, check_point_file = os.path.split(self.best_model_file)
        check_point_path = Path(check_point_dir)

        # Copy all tf2 model files from the temp location to the final destination
        for f in check_point_path.glob(f"{check_point_file}*"):
            shutil.move(str(f.absolute()), model_file_name + f.suffix)

        # Generate the tf2 checkpoint file, copy+replace to ensure consistency
        dest_path, dest_file = os.path.split(model_file_name)
        with open(os.path.join(check_point_dir, "checkpoint")) as in_file, open(
            os.path.join(dest_path, "checkpoint"), "w"
        ) as out_file:
            for line in in_file:
                out_file.write(line.replace(check_point_file, dest_file))

        # Remove the old file
        check_point_path.joinpath("checkpoint").unlink()

    @classmethod
    def load(
        cls, model_file_name: Text, model_data_example: ConvoModelDataSet, *args, **kwargs
    ) -> "ConvoModel":
        logger.debug("Loading the model ...")
        # create empty model
        model = cls(*args, **kwargs)
        # need to train on 1 example to build weights of the correct size
        model.fit(
            model_data_example,
            epochs=1,
            batch_size=1,
            evaluate_every_num_epochs=0,
            evaluate_on_num_examples=0,
            batch_strategy=SEQUENTIAL,
            silent=True,  # don't confuse users with training output
            loading=True,  # don't use tensorboard while loading
            eager=True,  # no need to build tf graph, eager is faster here
        )
        # load trained weights
        model.load_weights(model_file_name)

        logger.debug("Finished loading the model.")
        return model

    def batch_loss_total(
        self, batch_in: Union[Tuple[tf.Tensor], Tuple[np.ndarray]]
    ) -> tf.Tensor:
        """Calculate total loss"""

        predict_loss = self.batch_loss(batch_in)
        loss_regularizarion = tf.math.add_n(self.losses)
        loss_total = predict_loss + loss_regularizarion
        self.total_loss.update_state(loss_total)

        return loss_total

    def batch_loop(
        self,
        dataset_function: Callable,
        call_model_function: Callable,
        batch_size: int,
        training: bool,
        offset: int,
        writer: Optional["ResourceSummaryWriter"] = None,
    ) -> int:
        """Run on batches"""
        self.reset_metrics()

        stage = offset

        self._training = training  # needed for eager mode
        for batch_in in dataset_function(batch_size):
            call_model_function(batch_in)

            if not self.tensorboard_log_on_epochs:
                self.log_metrics_for_tensor_board(stage, writer)

            stage += 1

        return stage

    @staticmethod
    def get_tf_call_model_func(
        dataset_function: Callable,
        call_model_function: Callable,
        eager: bool,
        phase: Text,
    ) -> Callable:
        """Convert functions to tensorflow functions"""

        if eager:
            return call_model_function

        logger.debug(f"Building tensorflow {phase} graph...")

        initialize_dataset = dataset_function(1)
        tf_call_model_func = tf.function(
            call_model_function, input_signature=[initialize_dataset.element_spec]
        )
        tf_call_model_func(next(iter(initialize_dataset)))

        logger.debug(f"Finished building tensorflow {phase} graph.")

        return tf_call_model_func

    def get_tf_train_funcs(
        self, eager: bool, model_data: ConvoModelDataSet, batch_strategy: Text
    ) -> Tuple[Callable, Callable]:
        """Create train tensorflow functions"""

        def train_data_set_func(_batch_size: int) -> tf.data.Dataset:
            return model_data.as_tf_data_set(_batch_size, batch_strategy, shuffle=True)

        self._training = True  # needed for tf graph mode
        return (
            train_data_set_func,
            self.get_tf_call_model_func(
                train_data_set_func, self.batch_training, eager, "train"
            ),
        )

    def get_tf_evaluation_func(
        self, eager: bool, evaluation_model_data: Optional[ConvoModelDataSet]
    ) -> Tuple[Optional[Callable], Optional[Callable]]:
        """Create evaluation tensorflow functions"""

        if evaluation_model_data is None:
            return None, None

        def evaluation_data_set_func(_batch_size: int) -> tf.data.Dataset:
            return evaluation_model_data.as_tf_data_set(
                _batch_size, SEQUENTIAL, shuffle=False
            )

        self._training = False  # needed for tf graph mode
        return (
            evaluation_data_set_func,
            self.get_tf_call_model_func(
                evaluation_data_set_func, self.batch_loss_total, eager, "evaluation"
            ),
        )

    def get_metric_res(self, affix: Optional[Text] = None) -> Dict[Text, Text]:
        """Get the metrics results"""
        affix = affix or ""

        return {
            f"{affix}{metric.name}": f"{metric.result().numpy():.3f}"
            for metric in self.metrics
            if metric.name in self.metrics_to_log
        }

    def log_metrics_for_tensor_board(
        self, step: int, writer: Optional["ResourceSummaryWriter"] = None
    ) -> None:
        if writer is not None:
            with writer.as_default():
                for metric in self.metrics:
                    if metric.name in self.metrics_to_log:
                        tf.summary.scalar(metric.name, metric.result(), step=step)

    def _does_model_enhance(self, current_results: Dict[Text, Text]) -> bool:
        # Initialize best_metrics_so_far with the first results
        if not self.best_metrics_so_far:
            keys_val = filter(
                lambda k: True if (k.endswith("_acc") or k.endswith("_f1")) else False,
                current_results.keys(),
            )
            for key in keys_val:
                self.best_metrics_so_far[key] = float(current_results[key])
            return True

        all_enhance = all(
            [
                float(current_results[key]) > self.best_metrics_so_far[key]
                for key in self.best_metrics_so_far.keys()
            ]
        )
        if all_enhance:
            for key in self.best_metrics_so_far.keys():
                self.best_metrics_so_far[key] = float(current_results[key])
        return all_enhance

    def save_model_check_point(
        self, current_results: Dict[Text, Text], epoch: int
    ) -> None:
        if self.checkpoint_model and self._does_model_enhance(current_results):
            logger.debug(f"Creating model checkpoint at epoch={epoch + 1}...")
            self.best_model_epoch = epoch + 1
            self.save(self.best_model_file, overwrite=True)

    @staticmethod
    def should_eval(
        evaluate_every_num_epochs: int, epochs: int, current_active_epoch: int
    ) -> bool:
        return (
                current_active_epoch == 0
                or (current_active_epoch + 1) % evaluate_every_num_epochs == 0
                or (current_active_epoch + 1) == epochs
        )

    @staticmethod
    def batch_to_model_data_set_format(
        batch: Union[Tuple[tf.Tensor], Tuple[np.ndarray]],
        data_signature: Dict[Text, Dict[Text, List[FeatureSign]]],
    ) -> Dict[Text, Dict[Text, List[tf.Tensor]]]:
        """Convert input batch tensors into batch data format.

        Batch contains any number of batch data. The order is equal to the
        key-value pairs in session data. As sparse data were converted into indices,
        data, shape before, this methods converts them into sparse tensors. Dense data
        is kept.
        """

        batch_data_set = defaultdict(lambda: defaultdict(list))

        index = 0
        for key, values in data_signature.items():
            for sub_key, signature in values.items():
                for is_sparse, feature_dimension in signature:
                    if is_sparse:
                        # explicitly substitute last dimension in shape with known
                        # static value
                        batch_data_set[key][sub_key].append(
                            tf.SparseTensor(
                                batch[index],
                                batch[index + 1],
                                [
                                    batch[index + 2][0],
                                    batch[index + 2][1],
                                    feature_dimension,
                                ],
                            )
                        )
                        index += 3
                    else:
                        if isinstance(batch[index], tf.Tensor):
                            batch_data_set[key][sub_key].append(batch[index])
                        else:
                            # convert to Tensor
                            batch_data_set[key][sub_key].append(
                                tf.constant(batch[index], dtype=tf.float32)
                            )
                        index += 1

        return batch_data_set

    @staticmethod
    def increasing_batch_size_linearly(
        epoch: int, batch_size: Union[List[int], int], epochs: int
    ) -> int:
        """Linearly increase batch size with every epoch.

        The idea comes from https://arxiv.org/abs/1711.00489.
        """

        if not isinstance(batch_size, list):
            return int(batch_size)

        if epochs > 1:
            return int(
                batch_size[0] + epoch * (batch_size[1] - batch_size[0]) / (epochs - 1)
            )
        else:
            return int(batch_size[0])

    def writing_model_summary(self):
        total_no_of_vars = np.sum(
            [np.prod(v.shape) for v in self.trainable_variables]
        )
        films = [
            f"{layer.name} ({layer.dtype.name}) "
            f"[{'x'.join(str(s) for s in layer.shape)}]"
            for layer in self.trainable_variables
        ]
        films.reverse()

        with open(self.model_summary_file, "w") as file:
            file.write("Variables: name (type) [shape]\n\n")
            for layer in films:
                file.write(layer)
                file.write("\n")
            file.write("\n")
            file.write(f"Total size of variables: {total_no_of_vars}")

    def compile(self, *args, **kwargs) -> None:
        raise Exception(
            "This method should neither be called nor implemented in our code."
        )

    def evaluation(self, *args, **kwargs) -> None:
        raise Exception(
            "This method should neither be called nor implemented in our code."
        )

    def batch_testing(self, *args, **kwargs) -> None:
        raise Exception(
            "This method should neither be called nor implemented in our code."
        )

    def batch_prediction(self, *args, **kwargs) -> None:
        raise Exception(
            "This method should neither be called nor implemented in our code."
        )

    def fit_generator(self, *args, **kwargs) -> None:
        raise Exception(
            "This method should neither be called nor implemented in our code."
        )

    def generator_evaluation(self, *args, **kwargs) -> None:
        raise Exception(
            "This method should neither be called nor implemented in our code."
        )

    def generator_prediction(self, *args, **kwargs) -> None:
        raise Exception(
            "This method should neither be called nor implemented in our code."
        )

    def call(self, *args, **kwargs) -> None:
        raise Exception(
            "This method should neither be called nor implemented in our code."
        )

    def get_config(self) -> None:
        raise Exception(
            "This method should neither be called nor implemented in our code."
        )


# noinspection PyMethodOverriding
class ConverterConvoModel(ConvoModel):
    def __init__(
        self,
        name: Text,
        config: Dict[Text, Any],
        data_signature: Dict[Text, Dict[Text, List[FeatureSign]]],
        label_data: ConvoModelDataSet,
    ) -> None:
        super().__init__(
            name=name,
            random_seed=config[RAND_SEED],
            tensorboard_log_dir=config[TENSOR_BOARD_LOG_DIRECTORY],
            tensorboard_log_level=config[TENSOR_BOARD_LOGGING_LEVEL],
            checkpoint_model=config[CHECK_POINT_MODEL],
        )

        self.config = config
        self.data_signature = data_signature
        self.label_signature = label_data.get_sign()

        self._check_data()       
        labelled_batch = label_data.preparing_batch_data()        
        self.tf_label_data = self.batch_to_model_data_set_format(
            labelled_batch, self.label_signature
        )

        # set up tf layers
        self._tf_layers: Dict[Text : tf.keras.layers.Layer] = {}

    def _check_data(self) -> None:
        raise NotImplementedError

    def _prepare_layers(self) -> None:
        raise NotImplementedError

    def preparing_embedding_layers(self, name: Text, prefix: Text = "embed") -> None:
        self._tf_layers[f"{prefix}.{name}"] = layers.implanted(
            self.config[EMBEDDING_CAPACITY],
            self.config[REGULARIZATION_CONST],
            name,
            self.config[SIMILARITY_TYPE_CATEGORY],
        )

    def ffnn_layer_preparation(
        self,
        name: Text,
        layer_sizes: List[int],
        drop_rate: float,
        prefix: Text = "ffnn",
    ) -> None:
        self._tf_layers[f"{prefix}.{name}"] = layers.Ffnn(
            layer_sizes,
            drop_rate,
            self.config[REGULARIZATION_CONST],
            self.config[WEIGHT_SPARSE],
            layer_name_suffix=name,
        )

    def transformer_layer_preparation(
        self,
        name: Text,
        drop_rate: float,
        drop_rate_attention: float,
        prefix: Text = "transformer",
    ):
        if self.config[NUMBER_TRANSFORMER_LAYERS] > 0:
            self._tf_layers[f"{prefix}.{name}"] = ConverterEncoder(
                self.config[NUMBER_TRANSFORMER_LAYERS],
                self.config[TRANSFORMER_DIMENSION],
                self.config[NUMBER_HEADS],
                self.config[TRANSFORMER_DIMENSION] * 4,
                self.config[REGULARIZATION_CONST],
                dropout_rate=drop_rate,
                attention_dropout_rate=drop_rate_attention,
                sparsity=self.config[WEIGHT_SPARSE],
                unidirectional=self.config[UNI_DIRECTIONAL_ENCODER],
                use_key_relative_position=self.config[RELATIVE_ATTENTION_KEY],
                use_value_relative_position=self.config[RELATIVE_ATTENTION_VAL],
                max_relative_position=self.config[RELATIVE_POSITION_MAXIMUM],
                name=f"{name}_encoder",
            )
        else:
            # create lambda so that it can be used later without the check
            self._tf_layers[f"{prefix}.{name}"] = lambda x, mask, training: x

    def dot_product_loss_preparation(
        self, name: Text, scale_loss: bool, prefix: Text = "loss"
    ) -> None:
        self._tf_layers[f"{prefix}.{name}"] = layers.LossingDotProduct(
            self.config[NUMBER_NEG],
            self.config[LOSS_CATEGORY],
            self.config[MAXIMUM_POSITIVE_SIMILARITY],
            self.config[MAXIMUM_NEGATIVE_SIMILARITY],
            self.config[USE_MAXIMUM_NEGATIVE_SIMILARITY],
            self.config[NEG_MARGIN_SCALE],
            scale_loss,
            # set to 1 to get deterministic behaviour
            parallel_iterations=1 if self.random_seed is not None else 1000,
        )

    def sparse_dense_dropout_layers_preparation(
        self, name: Text, drop_rate: float
    ) -> None:
        self._tf_layers[f"sparse_input_dropout.{name}"] = layers.SparsePullout(
            rate=drop_rate
        )
        self._tf_layers[f"dense_input_dropout.{name}"] = tf.keras.layers.Dropout(
            rate=drop_rate
        )

    def sparse_dense_layers_preparation(
        self, data_signature: List[FeatureSign], name: Text, dense_dim: int
    ) -> None:
        infrequent = False
        frequent = False
        for is_sparse, _ in data_signature:
            if is_sparse:
                infrequent = True
            else:
                frequent = True

        if infrequent:
            self._tf_layers[f"sparse_to_dense.{name}"] = layers.CondenseForSparse(
                units=dense_dim,
                reg_lambda=self.config[REGULARIZATION_CONST],
                name=name,
            )
            if not frequent:
                # create dense labels for the input to use in negative sampling
                self._tf_layers[f"sparse_to_dense_ids.{name}"] = layers.CondenseForSparse(
                    units=2, trainable=False, name=f"sparse_to_dense_ids.{name}"
                )

    def _combine_sparse_dense_features(
        self,
        features: List[Union[np.ndarray, tf.Tensor, tf.SparseTensor]],
        name: Text,
        mask: Optional[tf.Tensor] = None,
        sparse_dropout: bool = False,
        dense_dropout: bool = False,
    ) -> Optional[tf.Tensor]:

        if not features:
            return None

        dense_ftrs = []

        for f in features:
            if isinstance(f, tf.SparseTensor):
                if sparse_dropout:
                    _g = self._tf_layers[f"sparse_input_dropout.{name}"](
                        f, self._training
                    )
                else:
                    _g = f

                frequent_f = self._tf_layers[f"sparse_to_dense.{name}"](_g)

                if dense_dropout:
                    frequent_f = self._tf_layers[f"dense_input_dropout.{name}"](
                        frequent_f, self._training
                    )

                dense_ftrs.append(frequent_f)
            else:
                dense_ftrs.append(f)

        if mask is None:
            return tf.concat(dense_ftrs, axis=-1)

        return tf.concat(dense_ftrs, axis=-1) * mask

    @staticmethod
    def computing_mask(sequence_lengths: tf.Tensor) -> tf.Tensor:
        covered = tf.sequence_mask(sequence_lengths, dtype=tf.float32)
        # explicitly add last dimension to mask
        # to track correctly dynamic sequences
        return tf.expand_dims(covered, -1)

    @staticmethod
    def end_token(x: tf.Tensor, sequence_lengths: tf.Tensor) -> tf.Tensor:
        end_sequence_index = tf.maximum(0, sequence_lengths - 1)
        batch_idx = tf.range(tf.shape(end_sequence_index)[0])

        indexes = tf.stack([batch_idx, end_sequence_index], axis=1)
        return tf.gather_nd(x, indexes)

    def getting_mask(
        self,
        tf_batch_data: Dict[Text, Dict[Text, List[tf.Tensor]]],
        key: Text,
        sub_key: Text,
    ) -> Optional[tf.Tensor]:
        if key not in tf_batch_data or sub_key not in tf_batch_data[key]:
            return None

        sequence_lens = tf.cast(tf_batch_data[key][sub_key][0], dtype=tf.int32)
        return self.computing_mask(sequence_lens)

    def batch_loss(
        self, batch_in: Union[Tuple[tf.Tensor], Tuple[np.ndarray]]
    ) -> tf.Tensor:
        raise NotImplementedError

    def batch_predict(
        self, batch_in: Union[Tuple[tf.Tensor], Tuple[np.ndarray]]
    ) -> Dict[Text, tf.Tensor]:
        raise NotImplementedError
