import logging
from typing import List, Optional, Text, Tuple, Callable, Union, Any
import tensorflow as tf
import tensorflow_addons as tfa
import convo.utils.tensorflow.crf
from tensorflow.python.keras.utils import tf_utils
from tensorflow.python.keras import backend as K
from convo.utils.tensorflow.constants import SOFT_MAX, EDGE, COSINE_VALUE, INTERIOR

log = logging.getLogger(__name__)

# https://github.com/tensorflow/addons#gpu-and-cpu-custom-ops-1
tfa.options.TF_ADDONS_PY_OPS = True


class SparsePullout(tf.keras.layers.Dropout):
    """Applies Dropout to the input.

    Dropout consists in randomly setting
    a fraction `rate` of input units to 0 at each update during training time,
    which helps prevent overfitting.

    Arguments:
        rate: Float between 0 and 1; fraction of the input units to drop.
    """

    def call(
        self, inputs: tf.SparseTensor, train: Optional[Union[tf.Tensor, bool]] = None
    ) -> tf.SparseTensor:
        """Apply dropout to sparse inputs.

        Arguments:
            inputs: Input sparse tensor (of any rank).
            train: Python boolean indicating whether the layer should behave in
                training mode (adding dropout) or in inference mode (doing nothing).

        Returns:
            Output of dropout layer.

        Raises:
            A ValueError if inputs is not a sparse tensor
        """

        if not isinstance(inputs, tf.SparseTensor):
            raise ValueError("Input tensor should be sparse.")

        if train is None:
            train = K.learning_phase()

        def drop_input_val() -> tf.SparseTensor:
            retaining_prob = tf.random.uniform(
                tf.shape(inputs.values), 0, 1, inputs.values.dtype
            )
            to_recover = tf.greater_equal(retaining_prob, self.rate)
            return tf.sparse.retain(inputs, to_recover)

        results = tf_utils.smart_cond(
            train, drop_input_val, lambda: tf.identity(inputs)
        )
        # need to explicitly recreate sparse tensor, because otherwise the shape
        # information will be lost after `retain`
        # noinspection PyProtectedMember
        return tf.SparseTensor(results.indices, results.values, inputs._dense_shape)


class CondenseForSparse(tf.keras.layers.Dense):
    """Dense layer for sparse input tensor.

    Just your regular densely-connected NN layer but for sparse tensors.

    `Dense` implements the operation:
    `output = activation(dot(input, kernel) + bias)`
    where `activation` is the element-wise activation function
    passed as the `activation` argument, `kernel` is a weights matrix
    created by the layer, and `bias` is a bias vector created by the layer
    (only applicable if `use_bias` is `True`).

    Note: If the input to the layer has a rank greater than 2, then
    it is flattened prior to the initial dot product with `kernel`.

    Arguments:
        units: Positive integer, dimensionality of the output space.
            activation: Activation function to use.
            If you don't specify anything, no activation is applied
            (ie. "linear" activation: `a(x) = x`).
        use_bias: Boolean, whether the layer uses a bias vector.
        kernel_initializer: Initializer for the `kernel` weights matrix.
        bias_initializer: Initializer for the bias vector.
        reg_lambda: Float, regularization factor.
        bias_regularizer: Regularizer function applied to the bias vector.
        activity_regularizer: Regularizer function applied to
            the output of the layer (its "activation")..
        kernel_constraint: Constraint function applied to
            the `kernel` weights matrix.
        bias_constraint: Constraint function applied to the bias vector.

    Input shape:
        N-D tensor with shape: `(batch_size, ..., input_dim)`.
        The most common situation would be
        a 2D input with shape `(batch_size, input_dim)`.

    Output shape:
        N-D tensor with shape: `(batch_size, ..., units)`.
        For instance, for a 2D input with shape `(batch_size, input_dim)`,
        the output would have shape `(batch_size, units)`.
    """

    def __init__(self, reg_lambda: float = 0, **kwargs: Any) -> None:
        if reg_lambda > 0:
            structurizer = tf.keras.regularizers.l2(reg_lambda)
        else:
            structurizer = None

        super().__init__(kernel_regularizer=structurizer, **kwargs)

    def call(self, inputs: tf.SparseTensor) -> tf.Tensor:
        """Apply dense layer to sparse inputs.

        Arguments:
            inputs: Input sparse tensor (of any rank).

        Returns:
            Output of dense layer.

        Raises:
            A ValueError if inputs is not a sparse tensor
        """
        if not isinstance(inputs, tf.SparseTensor):
            raise ValueError("Input tensor should be sparse.")

        # outputs will be 2D
        results = tf.sparse.sparse_dense_matmul(
            tf.sparse.reshape(inputs, [-1, tf.shape(inputs)[-1]]), self.kernel
        )

        if len(inputs.shape) == 3:
            # reshape back
            results = tf.reshape(
                results, (tf.shape(inputs)[0], tf.shape(inputs)[1], -1)
            )

        if self.use_bias:
            results = tf.nn.bias_add(results, self.bias)
        if self.activation is not None:
            return self.activation(results)
        return results


class CondenseWithSparseWeights(tf.keras.layers.Dense):
    """Just your regular densely-connected NN layer but with sparse weights.

    `Dense` implements the operation:
    `output = activation(dot(input, kernel) + bias)`
    where `activation` is the element-wise activation function
    passed as the `activation` argument, `kernel` is a weights matrix
    created by the layer, and `bias` is a bias vector created by the layer
    (only applicable if `use_bias` is `True`).
    It creates `kernel_mask` to set fraction of the `kernel` weights to zero.

    Note: If the input to the layer has a rank greater than 2, then
    it is flattened prior to the initial dot product with `kernel`.

    Arguments:
        sparsity: Float between 0 and 1. Fraction of the `kernel`
            weights to set to zero.
        units: Positive integer, dimensionality of the output space.
        activation: Activation function to use.
            If you don't specify anything, no activation is applied
            (ie. "linear" activation: `a(x) = x`).
        use_bias: Boolean, whether the layer uses a bias vector.
        kernel_initializer: Initializer for the `kernel` weights matrix.
        bias_initializer: Initializer for the bias vector.
        kernel_regularizer: Regularizer function applied to
            the `kernel` weights matrix.
        bias_regularizer: Regularizer function applied to the bias vector.
        activity_regularizer: Regularizer function applied to
            the output of the layer (its "activation")..
        kernel_constraint: Constraint function applied to
            the `kernel` weights matrix.
        bias_constraint: Constraint function applied to the bias vector.

    Input shape:
        N-D tensor with shape: `(batch_size, ..., input_dim)`.
        The most common situation would be
        a 2D input with shape `(batch_size, input_dim)`.

    Output shape:
        N-D tensor with shape: `(batch_size, ..., units)`.
        For instance, for a 2D input with shape `(batch_size, input_dim)`,
        the output would have shape `(batch_size, units)`.
    """

    def __init__(self, sparsity: float = 0.8, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.sparsity = sparsity

    def build(self, input_shape: tf.TensorShape) -> None:
        super().build(input_shape)
        # create random mask to set fraction of the `kernel` weights to zero
        mask_kernel = tf.random.uniform(tf.shape(self.kernel), 0, 1)
        mask_kernel = tf.cast(
            tf.greater_equal(mask_kernel, self.sparsity), self.kernel.dtype
        )
        self.kernel_mask = tf.Variable(
            initial_value=mask_kernel, trainable=False, name="mask_kernel"
        )

    def call(self, inputs: tf.Tensor) -> tf.Tensor:
        # set fraction of the `kernel` weights to zero according to precomputed mask
        self.kernel.assign(self.kernel * self.kernel_mask)
        return super().call(inputs)


class Ffnn(tf.keras.layers.Layer):
    """Feed-forward network layer.

    Arguments:
        layer_sizes: List of integers with dimensionality of the layers.
        dropout_rate: Float between 0 and 1; fraction of the input units to drop.
        reg_lambda: Float, regularization factor.
        sparsity: Float between 0 and 1. Fraction of the `kernel`
            weights to set to zero.
        layer_name_suffix: Text added to the name of the layers.

    Input shape:
        N-D tensor with shape: `(batch_size, ..., input_dim)`.
        The most common situation would be
        a 2D input with shape `(batch_size, input_dim)`.

    Output shape:
        N-D tensor with shape: `(batch_size, ..., layer_sizes[-1])`.
        For instance, for a 2D input with shape `(batch_size, input_dim)`,
        the output would have shape `(batch_size, layer_sizes[-1])`.
    """

    def __init__(
        self,
        layer_sizes: List[int],
        dropout_rate: float,
        reg_lambda: float,
        sparsity: float,
        layer_name_suffix: Text,
    ) -> None:
        super().__init__(name=f"ffnn_{layer_name_suffix}")

        l2_structurizer = tf.keras.regularizers.l2(reg_lambda)
        self._ffn_layers = []
        for i, layer_size in enumerate(layer_sizes):
            self._ffn_layers.append(
                CondenseWithSparseWeights(
                    units=layer_size,
                    sparsity=sparsity,
                    activation=tfa.activations.gelu,
                    kernel_regularizer=l2_structurizer,
                    name=f"hidden_layer_{layer_name_suffix}_{i}",
                )
            )
            self._ffn_layers.append(tf.keras.layers.Dropout(dropout_rate))

    def call(
        self, y: tf.Tensor, training: Optional[Union[tf.Tensor, bool]] = None
    ) -> tf.Tensor:
        for layer in self._ffn_layers:
            y = layer(y, training=training)

        return y


class implanted(tf.keras.layers.Layer):
    """Dense embedding layer.

    Arguments:
        embed_dim: Positive integer, dimensionality of the output space.
        reg_lambda: Float; regularization factor.
        layer_name_suffix: Text added to the name of the layers.
        similarity_type: Optional type of similarity measure to use,
            either 'cosine' or 'inner'.

    Input shape:
        N-D tensor with shape: `(batch_size, ..., input_dim)`.
        The most common situation would be
        a 2D input with shape `(batch_size, input_dim)`.

    Output shape:
        N-D tensor with shape: `(batch_size, ..., embed_dim)`.
        For instance, for a 2D input with shape `(batch_size, input_dim)`,
        the output would have shape `(batch_size, embed_dim)`.
    """

    def __init__(
        self,
        embed_dim: int,
        reg_lambda: float,
        layer_name_suffix: Text,
        similarity_type: Optional[Text] = None,
    ) -> None:
        super().__init__(name=f"embed_{layer_name_suffix}")

        self.similarity_type = similarity_type
        if self.similarity_type and self.similarity_type not in {COSINE_VALUE, INTERIOR}:
            raise ValueError(
                f"Wrong similarity type '{self.similarity_type}', "
                f"should be '{COSINE_VALUE}' or '{INTERIOR}'."
            )

        structurizer = tf.keras.regularizers.l2(reg_lambda)
        self._dense = tf.keras.layers.Dense(
            units=embed_dim,
            activation=None,
            kernel_regularizer=structurizer,
            name=f"embed_layer_{layer_name_suffix}",
        )

    # noinspection PyMethodOverriding
    def call(self, y: tf.Tensor) -> tf.Tensor:
        y = self._dense(y)
        if self.similarity_type == COSINE_VALUE:
            y = tf.nn.l2_normalize(y, axis=-1)

        return y


class MaskInput(tf.keras.layers.Layer):
    """The layer that masks 15% of the input.

    Input shape:
        N-D tensor with shape: `(batch_size, ..., input_dim)`.
        The most common situation would be
        a 2D input with shape `(batch_size, input_dim)`.

    Output shape:
        N-D tensor with shape: `(batch_size, ..., input_dim)`.
        For instance, for a 2D input with shape `(batch_size, input_dim)`,
        the output would have shape `(batch_size, input_dim)`.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self._masking_prob = 0.85
        self._mask_vector_prob = 0.7
        self._random_vector_prob = 0.1

    def build(self, input_shape: tf.TensorShape) -> None:
        self.mask_vector = self.add_weight(
            shape=(1, 1, input_shape[-1]), name="mask_vector"
        )
        self.built = True

    # noinspection PyMethodOverriding
    def call(
        self,
        x: tf.Tensor,
        mask: tf.Tensor,
        train: Optional[Union[tf.Tensor, bool]] = None,
    ) -> Tuple[tf.Tensor, tf.Tensor]:
        """Randomly mask input sequences.

        Arguments:
            x: Input sequence tensor of rank 3.
            mask: A tensor representing sequence mask,
                contains `1` for inputs and `0` for padding.
            train: Python boolean indicating whether the layer should behave in
                training mode (mask inputs) or in inference mode (doing nothing).

        Returns:
            A tuple of masked inputs and boolean mask.
        """

        if train is None:
            train = K.learning_phase()

        lm_mask_probability = tf.random.uniform(tf.shape(mask), 0, 1, mask.dtype) * mask
        lm_mask_boolean = tf.greater_equal(lm_mask_probability, self._masking_prob)

        def y_masked() -> tf.Tensor:
            y_random_pad = tf.random.uniform(
                tf.shape(x), tf.reduce_min(x), tf.reduce_max(x), x.dtype
            ) * (1 - mask)
            # shuffle over batch dim
            y_shuffle = tf.random.shuffle(x * mask + y_random_pad)

            # shuffle over sequence dim
            y_shuffle = tf.transpose(y_shuffle, [1, 0, 2])
            y_shuffle = tf.random.shuffle(y_shuffle)
            y_shuffle = tf.transpose(y_shuffle, [1, 0, 2])

            # shuffle doesn't support backprop
            y_shuffle = tf.stop_gradient(y_shuffle)

            masking_vector = tf.tile(self.mask_vector, (tf.shape(x)[0], tf.shape(x)[1], 1))

            other_problem = tf.random.uniform(tf.shape(mask), 0, 1, mask.dtype)
            other_problem = tf.tile(other_problem, (1, 1, x.shape[-1]))
            y_other = tf.where(
                other_problem < self._mask_vector_prob,
                masking_vector,
                tf.where(
                    other_problem < self._mask_vector_prob + self._random_vector_prob,
                    y_shuffle,
                    x,
                ),
            )

            return tf.where(tf.tile(lm_mask_boolean, (1, 1, x.shape[-1])), y_other, x)

        return (
            tf_utils.smart_cond(train, y_masked, lambda: tf.identity(x)),
            lm_mask_boolean,
        )


def loss_scale(log_likelihood: tf.Tensor) -> tf.Tensor:
    """Creates scaling loss coefficient depending on the prediction probability.

    Arguments:
        log_likelihood: a tensor, log-likelihood of prediction

    Returns:
        Scaling tensor.
    """

    q = tf.math.exp(log_likelihood)
    # only scale loss if some examples are already learned
    return tf.cond(
        tf.reduce_max(q) > 0.5,
        lambda: tf.stop_gradient(tf.pow((1 - q) / 0.5, 4)),
        lambda: tf.ones_like(q),
    )


class ConditionalRandomFields(tf.keras.layers.Layer):
    """ConditionalRandomFields layer.

    Arguments:
        num_tags: Positive integer, number of tags.
        reg_lambda: Float; regularization factor.
        name: Optional name of the layer.
    """

    def __init__(
        self,
        num_tags: int,
        reg_lambda: float,
        scale_loss: bool,
        name: Optional[Text] = None,
    ) -> None:
        super().__init__(name=name)
        self.num_tags = num_tags
        self.scale_loss = scale_loss
        self.transition_regularizer = tf.keras.regularizers.l2(reg_lambda)
        self.f1_score_metric = tfa.metrics.F1Score(
            num_classes=num_tags - 1,  # `0` prediction is not a prediction
            average="micro",
        )

    def build(self, input_shape: tf.TensorShape) -> None:
        # the weights should be created in `build` to apply random_seed
        self.transition_params = self.add_weight(
            shape=(self.num_tags, self.num_tags),
            regularizer=self.transition_regularizer,
            name="transitions",
        )
        self.built = True

    # noinspection PyMethodOverriding
    def call(
        self, logits: tf.Tensor, sequence_lengths: tf.Tensor
    ) -> Tuple[tf.Tensor, tf.Tensor]:
        """Decodes the highest scoring sequence of tags.

        Arguments:
            logits: A [batch_size, max_seq_len, num_tags] tensor of
                unary potentials.
            sequence_lengths: A [batch_size] vector of true sequence lengths.

        Returns:
            A [batch_size, max_seq_len] matrix, with dtype `tf.int32`.
            Contains the highest scoring tag indices.
            A [batch_size, max_seq_len] matrix, with dtype `tf.float32`.
            Contains the confidence values of the highest scoring tag indices.
        """
        ids_predicted, scores_val, _ = convo.utils.tensorflow.crf.conditional_random_field_decode(
            logits, self.transition_params, sequence_lengths
        )
        # set prediction index for padding to `0`
        cover = tf.sequence_mask(
            sequence_lengths,
            maxlen=tf.shape(ids_predicted)[1],
            dtype=ids_predicted.dtype,
        )

        confidence_vals = scores_val * tf.cast(cover, tf.float32)
        ids_predicted = ids_predicted * cover

        return ids_predicted, confidence_vals

    def data_loss(
        self, logits: tf.Tensor, tag_indices: tf.Tensor, sequence_lengths: tf.Tensor
    ) -> tf.Tensor:
        """Computes the log-likelihood of tag sequences in a ConditionalRandomFields.

        Arguments:
            logits: A [batch_size, max_seq_len, num_tags] tensor of unary potentials
                to use as input to the ConditionalRandomFields layer.
            tag_indices: A [batch_size, max_seq_len] matrix of tag indices for which
                we compute the log-likelihood.
            sequence_lengths: A [batch_size] vector of true sequence lengths.

        Returns:
            Negative mean log-likelihood of all examples,
            given the sequence of tag indices.
        """

        likelihood_log, _ = tfa.text.crf.crf_log_likelihood(
            logits, tag_indices, sequence_lengths, self.transition_params
        )
        data_loss = -likelihood_log
        if self.scale_loss:
            data_loss *= loss_scale(likelihood_log)

        return tf.reduce_mean(data_loss)

    def f1_score(
        self, tag_ids: tf.Tensor, pred_ids: tf.Tensor, mask: tf.Tensor
    ) -> tf.Tensor:
        """Calculates f1 score for train predictions"""

        mask_boolean = tf.cast(mask[:, :, 0], tf.bool)

        # pick only non padding values and flatten sequences
        label_ids_flat = tf.boolean_mask(tag_ids, mask_boolean)
        predicted_ids_flat = tf.boolean_mask(pred_ids, mask_boolean)

        # set `0` prediction to not a prediction
        number_tags = self.num_tags - 1

        label_ids_flat_one_hot = tf.one_hot(label_ids_flat - 1, number_tags)
        predicted_ids_flat_one_hot = tf.one_hot(predicted_ids_flat - 1, number_tags)

        return self.f1_score_metric(label_ids_flat_one_hot, predicted_ids_flat_one_hot)


class LossingDotProduct(tf.keras.layers.Layer):
    """Dot-product loss layer.

    Arguments:
        num_neg: Positive integer, the number of incorrect labels;
            the algorithm will minimize their similarity to the input.
        loss_type: The type of the loss function, either 'softmax' or 'margin'.
        mu_pos: Float, indicates how similar the algorithm should
            try to make embedding vectors for correct labels;
            should be 0.0 < ... < 1.0 for 'cosine' similarity type.
        mu_neg: Float, maximum negative similarity for incorrect labels,
            should be -1.0 < ... < 1.0 for 'cosine' similarity type.
        use_max_sim_neg: Boolean, if 'True' the algorithm only minimizes
            maximum similarity over incorrect intent labels,
            used only if 'loss_type' is set to 'margin'.
        neg_lambda: Float, the scale of how important is to minimize
            the maximum similarity between embeddings of different labels,
            used only if 'loss_type' is set to 'margin'.
        scale_loss: Boolean, if 'True' scale loss inverse proportionally to
            the confidence of the correct prediction.
        name: Optional name of the layer.
        parallel_iterations: Positive integer, the number of iterations allowed
            to run in parallel.
        same_sampling: Boolean, if 'True' sample same negative labels
            for the whole batch.
    """

    def __init__(
        self,
        num_neg: int,
        loss_type: Text,
        mu_pos: float,
        mu_neg: float,
        use_max_sim_neg: bool,
        neg_lambda: float,
        scale_loss: bool,
        name: Optional[Text] = None,
        parallel_iterations: int = 1000,
        same_sampling: bool = False,
    ) -> None:
        super().__init__(name=name)
        self.num_neg = num_neg
        self.loss_type = loss_type
        self.mu_pos = mu_pos
        self.mu_neg = mu_neg
        self.use_max_sim_neg = use_max_sim_neg
        self.neg_lambda = neg_lambda
        self.scale_loss = scale_loss
        self.parallel_iterations = parallel_iterations
        self.same_sampling = same_sampling

    @staticmethod
    def make_flat(x: tf.Tensor) -> tf.Tensor:
        """Make tensor 2D."""

        return tf.reshape(x, (-1, x.shape[-1]))

    def random_indexes(
        self, batch_size: tf.Tensor, total_candidates: tf.Tensor
    ) -> tf.Tensor:
        def rand_idxs() -> tf.Tensor:
            """Create random tensor of indices"""

            # (1, num_neg)
            return tf.expand_dims(
                tf.random.shuffle(tf.range(total_candidates))[: self.num_neg], 0
            )

        if self.same_sampling:
            return tf.tile(rand_idxs(), (batch_size, 1))

        def condition(idx: tf.Tensor, out: tf.Tensor) -> tf.Tensor:
            """Condition for while loop"""
            return idx < batch_size

        def content(idx: tf.Tensor, out: tf.Tensor) -> List[tf.Tensor]:
            """Body of the while loop"""
            return [
                # increment counter
                idx + 1,
                # add random indices
                tf.concat([out, rand_idxs()], 0),
            ]

        # first tensor already created
        index1 = tf.constant(1)
        # create first random array of indices
        output1 = rand_idxs()  # (1, num_neg)

        return tf.while_loop(
            condition,
            content,
            loop_vars=[index1, output1],
            shape_invariants=[index1.shape, tf.TensorShape([None, self.num_neg])],
            parallel_iterations=self.parallel_iterations,
            back_prop=False,
        )[1]

    @staticmethod
    def sample_indexes(batch_size: tf.Tensor, x: tf.Tensor, idxs: tf.Tensor) -> tf.Tensor:
        """Sample negative examples for given indices"""

        tiled_value = tf.tile(tf.expand_dims(x, 0), (batch_size, 1, 1))

        return tf.gather(tiled_value, idxs, batch_dims=1)

    def fetch_bad_mask(
        self, labels: tf.Tensor, target_labels: tf.Tensor, idxs: tf.Tensor
    ) -> tf.Tensor:
        """Calculate bad mask for given indices.

        Checks that input features are different for positive negative samples.
        """

        positive_labels = tf.expand_dims(target_labels, axis=-2)
        negative_labels = self.sample_indexes(tf.shape(target_labels)[0], labels, idxs)

        return tf.cast(
            tf.reduce_all(tf.equal(negative_labels, positive_labels), axis=-1), positive_labels.dtype
        )

    def get_negatives(
        self, embeds: tf.Tensor, labels: tf.Tensor, target_labels: tf.Tensor
    ) -> Tuple[tf.Tensor, tf.Tensor]:
        """Get negative examples from given tensor."""

        embedded_flat = self.make_flat(embeds)
        flat_labels = self.make_flat(labels)
        target_flat_labels = self.make_flat(target_labels)

        candidates_total = tf.shape(embedded_flat)[0]
        targetted_size = tf.shape(target_flat_labels)[0]

        negative_ids = self.random_indexes(targetted_size, candidates_total)

        negative_embeds = self.sample_indexes(targetted_size, embedded_flat, negative_ids)
        bad_negatives = self.fetch_bad_mask(flat_labels, target_flat_labels, negative_ids)

        # check if inputs have sequence dimension
        if len(target_labels.shape) == 3:
            # tensors were flattened for sampling, reshape back
            # add sequence dimension if it was present in the inputs
            targetted_shape = tf.shape(target_labels)
            negative_embeds = tf.reshape(
                negative_embeds, (targetted_shape[0], targetted_shape[1], -1, embeds.shape[-1])
            )
            bad_negatives = tf.reshape(bad_negatives, (targetted_shape[0], targetted_shape[1], -1))

        return negative_embeds, bad_negatives

    def negatives_sample(
        self,
        inputs_embed: tf.Tensor,
        labels_embed: tf.Tensor,
        labels: tf.Tensor,
        all_labels_embed: tf.Tensor,
        all_labels: tf.Tensor,
    ) -> Tuple[tf.Tensor, tf.Tensor, tf.Tensor, tf.Tensor, tf.Tensor, tf.Tensor]:
        """Sample negative examples."""

        positive_inputs_embed = tf.expand_dims(inputs_embed, axis=-2)
        positive_labels_embed = tf.expand_dims(labels_embed, axis=-2)

        # sample negative inputs
        negative_inputs_embed, input_bad_negatives = self.get_negatives(inputs_embed, labels, labels)
        # sample negative labels
        negatives_labels_embed, labels_bad_negatives = self.get_negatives(
            all_labels_embed, all_labels, labels
        )
        return (
            positive_inputs_embed,
            positive_labels_embed,
            negative_inputs_embed,
            negatives_labels_embed,
            input_bad_negatives,
            labels_bad_negatives,
        )

    @staticmethod
    def simulation(a: tf.Tensor, b: tf.Tensor, mask: Optional[tf.Tensor] = None) -> tf.Tensor:
        """Calculate similarity between given tensors."""

        simulation = tf.reduce_sum(a * b, axis=-1)
        if mask is not None:
            simulation *= tf.expand_dims(mask, 2)

        return simulation

    @staticmethod
    def confidence_from_simulation(sim: tf.Tensor, similarity_type: Text) -> tf.Tensor:
        if similarity_type == COSINE_VALUE:
            # clip negative values to zero
            return tf.nn.relu(sim)
        else:
            # normalize result to [0, 1] with softmax
            return tf.nn.softmax(sim)

    def training_sim(
        self,
        pos_inputs_embed: tf.Tensor,
        pos_labels_embed: tf.Tensor,
        neg_inputs_embed: tf.Tensor,
        neg_labels_embed: tf.Tensor,
        inputs_bad_negs: tf.Tensor,
        labels_bad_negs: tf.Tensor,
        mask: Optional[tf.Tensor],
    ) -> Tuple[tf.Tensor, tf.Tensor, tf.Tensor, tf.Tensor, tf.Tensor]:
        """Define similarity."""

        # calculate similarity with several
        # embedded actions for the loss
        negative_info = tf.constant(-1e9)

        sim_positive = self.simulation(pos_inputs_embed, pos_labels_embed, mask)
        sim_negative_il = (
            self.simulation(pos_inputs_embed, neg_labels_embed, mask)
            + negative_info * labels_bad_negs
        )
        sim_negative_ll = (
            self.simulation(pos_labels_embed, neg_labels_embed, mask)
            + negative_info * labels_bad_negs
        )
        sim_negative_ii = (
            self.simulation(pos_inputs_embed, neg_inputs_embed, mask)
            + negative_info * inputs_bad_negs
        )
        sim_negative_li = (
            self.simulation(pos_labels_embed, neg_inputs_embed, mask)
            + negative_info * inputs_bad_negs
        )

        # output similarities between user input and bot actions
        # and similarities between bot actions and similarities between user inputs
        return sim_positive, sim_negative_il, sim_negative_ll, sim_negative_ii, sim_negative_li

    @staticmethod
    def calculate_accuracy(sim_pos: tf.Tensor, sim_neg: tf.Tensor) -> tf.Tensor:
        """Calculate accuracy."""

        maximum_all_sim = tf.reduce_max(tf.concat([sim_pos, sim_neg], axis=-1), axis=-1)
        return tf.reduce_mean(
            tf.cast(
                tf.math.equal(maximum_all_sim, tf.squeeze(sim_pos, axis=-1)), tf.float32
            )
        )

    def margin_loss(
        self,
        sim_pos: tf.Tensor,
        sim_neg_il: tf.Tensor,
        sim_neg_ll: tf.Tensor,
        sim_neg_ii: tf.Tensor,
        sim_neg_li: tf.Tensor,
        mask: Optional[tf.Tensor],
    ) -> tf.Tensor:
        """Define max margin loss."""

        # loss for maximizing similarity with correct action
        data_loss = tf.maximum(0.0, self.mu_pos - tf.squeeze(sim_pos, axis=-1))

        # loss for minimizing similarity with `num_neg` incorrect actions
        if self.use_max_sim_neg:
            # minimize only maximum similarity over incorrect actions
            maximum_sim_negative_il = tf.reduce_max(sim_neg_il, axis=-1)
            data_loss += tf.maximum(0.0, self.mu_neg + maximum_sim_negative_il)
        else:
            # minimize all similarities with incorrect actions
            maximum_margin = tf.maximum(0.0, self.mu_neg + sim_neg_il)
            data_loss += tf.reduce_sum(maximum_margin, axis=-1)

        # penalize max similarity between pos bot and neg bot embeddings
        maximum_sim_negative_ll = tf.maximum(
            0.0, self.mu_neg + tf.reduce_max(sim_neg_ll, axis=-1)
        )
        data_loss += maximum_sim_negative_ll * self.neg_lambda

        # penalize max similarity between pos dial and neg dial embeddings
        maximum_sim_negative_ii = tf.maximum(
            0.0, self.mu_neg + tf.reduce_max(sim_neg_ii, axis=-1)
        )
        data_loss += maximum_sim_negative_ii * self.neg_lambda

        # penalize max similarity between pos bot and neg dial embeddings
        maximum_sim_negative_li = tf.maximum(
            0.0, self.mu_neg + tf.reduce_max(sim_neg_li, axis=-1)
        )
        data_loss += maximum_sim_negative_li * self.neg_lambda

        if mask is not None:
            # mask loss for different length sequences
            data_loss *= mask
            # average the loss over sequence length
            data_loss = tf.reduce_sum(data_loss, axis=-1) / tf.reduce_sum(mask, axis=1)

        # average the loss over the batch
        data_loss = tf.reduce_mean(data_loss)

        return data_loss

    def loss_soft_max(
        self,
        sim_pos: tf.Tensor,
        sim_neg_il: tf.Tensor,
        sim_neg_ll: tf.Tensor,
        sim_neg_ii: tf.Tensor,
        sim_neg_li: tf.Tensor,
        mask: Optional[tf.Tensor],
    ) -> tf.Tensor:
        """Define softmax loss."""

        logits = tf.concat(
            [sim_pos, sim_neg_il, sim_neg_ll, sim_neg_ii, sim_neg_li], axis=-1
        )

        # create ids_label for softmax
        ids_label = tf.zeros_like(logits[..., 0], tf.int32)

        data_loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
            labels=ids_label, logits=logits
        )

        if self.scale_loss:
            # in case of cross entropy log_likelihood = -loss
            data_loss *= loss_scale(-data_loss)

        if mask is not None:
            data_loss *= mask

        if len(data_loss.shape) == 2:
            # average over the sequence
            if mask is not None:
                data_loss = tf.reduce_sum(data_loss, axis=-1) / tf.reduce_sum(mask, axis=-1)
            else:
                data_loss = tf.reduce_mean(data_loss, axis=-1)

        # average the loss over the batch
        return tf.reduce_mean(data_loss)

    @property
    def loss_chosen(self) -> Callable:
        """Use loss depending on given option."""

        if self.loss_type == EDGE:
            return self.margin_loss
        elif self.loss_type == SOFT_MAX:
            return self.loss_soft_max
        else:
            raise ValueError(
                f"Wrong loss type '{self.loss_type}', "
                f"should be '{EDGE}' or '{SOFT_MAX}'"
            )

    # noinspection PyMethodOverriding
    def call(
        self,
        inputs_embed: tf.Tensor,
        labels_embed: tf.Tensor,
        labels: tf.Tensor,
        all_labels_embed: tf.Tensor,
        all_labels: tf.Tensor,
        mask: Optional[tf.Tensor] = None,
    ) -> Tuple[tf.Tensor, tf.Tensor]:
        """Calculate loss_val and accuracy_val.

        Arguments:
            inputs_embed: Embedding tensor for the batch inputs.
            labels_embed: Embedding tensor for the batch labels.
            labels: Tensor representing batch labels.
            all_labels_embed: Embedding tensor for the all labels.
            all_labels: Tensor representing all labels.
            mask: Optional tensor representing sequence mask,
                contains `1` for inputs and `0` for padding.

        Returns:
            loss_val: Total loss_val.
            accuracy_val: Training accuracy_val.
        """
        (
            pos_inputs_embed,
            pos_labels_embed,
            neg_inputs_embed,
            neg_labels_embed,
            inputs_bad_negs,
            labels_bad_negs,
        ) = self.negatives_sample(
            inputs_embed, labels_embed, labels, all_labels_embed, all_labels
        )

        # calculate similarities
        sim_pos, sim_neg_il, sim_neg_ll, sim_neg_ii, sim_neg_li = self.training_sim(
            pos_inputs_embed,
            pos_labels_embed,
            neg_inputs_embed,
            neg_labels_embed,
            inputs_bad_negs,
            labels_bad_negs,
            mask,
        )

        accuracy_val = self.calculate_accuracy(sim_pos, sim_neg_il)

        loss_val = self.loss_chosen(
            sim_pos, sim_neg_il, sim_neg_ll, sim_neg_ii, sim_neg_li, mask
        )

        return loss_val, accuracy_val
