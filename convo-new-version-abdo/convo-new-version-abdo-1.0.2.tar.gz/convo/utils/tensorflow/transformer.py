from typing import List, Optional, Text, Tuple, Union
import tensorflow as tf
import tensorflow_addons as tfa
from tensorflow.python.keras.utils import tf_utils
from tensorflow.python.keras import backend as K
import numpy as np
from convo.utils.tensorflow.layers import CondenseWithSparseWeights


# from https://www.tensorflow.org/tutorials/text/transformer
# and https://github.com/tensorflow/tensor2tensor
class ManyHeadAttention(tf.keras.layers.Layer):
    """Multi-headed attention layer.

    Arguments:
        units: Positive integer, output dim of hidden layer.
        num_heads: Positive integer, number of heads
            to repeat the same attention structure.
        attention_dropout_rate: Float, dropout rate inside attention for training.
        sparsity: Float between 0 and 1. Fraction of the `kernel`
            weights to set to zero.
        unidirectional: Boolean, use a unidirectional or bidirectional encoder.
        use_key_relative_position: Boolean, if 'True' use key
            relative embeddings in attention.
        use_value_relative_position: Boolean, if 'True' use value
            relative embeddings in attention.
        max_relative_position: Positive integer, max position for relative embeddings.
        heads_share_relative_embedding: Boolean, if 'True'
            heads will share relative embeddings.
    """

    def __init__(
        self,
        units: int,
        num_heads: int,
        attention_dropout_rate: float = 0.0,
        sparsity: float = 0.8,
        unidirectional: bool = False,
        use_key_relative_position: bool = False,
        use_value_relative_position: bool = False,
        max_relative_position: Optional[int] = None,
        heads_share_relative_embedding: bool = False,
    ) -> None:
        super().__init__()

        if units % num_heads != 0:
            raise ValueError(
                f"number of units {units} should be proportional to "
                f"number of attention heads {num_heads}."
            )

        self.num_heads = num_heads
        self.units = units
        self.attention_dropout_rate = attention_dropout_rate
        self.unidirectional = unidirectional
        self.use_key_relative_position = use_key_relative_position
        self.use_value_relative_position = use_value_relative_position
        self.relative_length = max_relative_position
        if self.relative_length is not None:
            self.relative_length += 1  # include current time
        self.heads_share_relative_embedding = heads_share_relative_embedding

        self._depth = units // self.num_heads

        # process queries
        self._query_dense_layer = CondenseWithSparseWeights(
            units=units, use_bias=False, sparsity=sparsity
        )
        # process keys
        self._key_dense_layer = CondenseWithSparseWeights(
            units=units, use_bias=False, sparsity=sparsity
        )
        # process values
        self._value_dense_layer = CondenseWithSparseWeights(
            units=units, use_bias=False, sparsity=sparsity
        )
        # process attention output
        self._output_dense_layer = CondenseWithSparseWeights(
            units=units, sparsity=sparsity
        )

        self._generate_relative_embeddings()

    def _generate_relative_embeddings(self) -> None:
        """Create relative embeddings."""

        shape_of_relative_embedding = None
        self.key_relative_embeddings = None
        self.value_relative_embeddings = None

        if self.use_key_relative_position or self.use_value_relative_position:
            if not self.relative_length:
                raise ValueError(
                    f"Max relative position {self.relative_length} "
                    f"should be > 0 when using relative attention."
                )

            if self.unidirectional:
                relative_len = self.relative_length
            else:
                relative_len = 2 * self.relative_length - 1

            if self.heads_share_relative_embedding:
                shape_of_relative_embedding = (relative_len, self._depth)
            else:
                shape_of_relative_embedding = (
                    self.num_heads,
                    relative_len,
                    self._depth,
                )

        if self.use_key_relative_position:
            self.key_relative_embeddings = self.add_weight(
                shape=shape_of_relative_embedding, name="key_relative_embeddings"
            )

        if self.use_value_relative_position:
            self.value_relative_embeddings = self.add_weight(
                shape=shape_of_relative_embedding, name="value_relative_embeddings"
            )

    def padding_relative_embeddings(self, x: tf.Tensor, length: tf.Tensor) -> tf.Tensor:
        # pad the left side to length
        left_padding = x[:, :, :, :1, :]
        left_padding = tf.tile(left_padding, (1, 1, 1, length - self.relative_length, 1))

        # pad the right side to length
        if self.unidirectional:
            relative_len_right = 1  # current time
            right_padding = tf.zeros_like(x[:, :, :, -1:, :])
        else:
            relative_len_right = self.relative_length
            right_padding = x[:, :, :, -1:, :]
        right_padding = tf.tile(right_padding, (1, 1, 1, length - relative_len_right, 1))

        return tf.concat([left_padding, x, right_padding], axis=-2)

    def slicing_relative_embeds(self, y: tf.Tensor, length: tf.Tensor) -> tf.Tensor:
        if self.unidirectional:
            # pad the right side to relative_length
            right_padding = tf.zeros_like(y[:, :, :, -1:, :])
            right_padding = tf.tile(right_padding, (1, 1, 1, self.relative_length - 1, 1))
            y = tf.concat([y, right_padding], axis=-2)

        extra_len = self.relative_length - length
        full_len = tf.shape(y)[-2]
        return y[:, :, :, extra_len: full_len - extra_len, :]

    def relative_to_absolute_pos(self, y: tf.Tensor) -> tf.Tensor:
        """Universal method to convert tensor from relative to absolute indexing.

        "Slides" relative embeddings by 45 degree.

        Arguments:
        x: A tensor of shape (batch, num_heads, length, relative_length, depth)
            or (batch, num_heads, length, relative_length)

        Returns:
            A tensor of shape (batch, num_heads, length, length, depth)
            or (batch, num_heads, length, length)
        """

        x_dimension = len(y.shape)

        if x_dimension < 4 or x_dimension > 5:
            raise ValueError(
                f"Relative tensor has a wrong shape {y.shape}, "
                f"it should have 4 or 5 dimensions."
            )
        if x_dimension == 4:
            # add fake depth dimension
            y = tf.expand_dims(y, axis=-1)

        group = tf.shape(y)[0]
        number_heads = tf.shape(y)[1]
        lens = tf.shape(y)[2]
        deepness = tf.shape(y)[-1]

        y = tf.cond(
            lens > self.relative_length,
            lambda: self.padding_relative_embeddings(y, lens),
            lambda: self.slicing_relative_embeds(y, lens),
        )

        # add a column of zeros to "slide" columns to diagonals through reshape
        pad_shifting = tf.zeros_like(y[:, :, :, -1:, :])
        y = tf.concat([y, pad_shifting], axis=-2)

        # flatten length dimensions
        y = tf.reshape(y, (group, number_heads, -1, deepness))
        breadth = 2 * lens

        # add zeros so that the result of back reshape is still a matrix
        flat_pad = tf.zeros_like(
            y[:, :, : ((breadth - 1) - breadth * lens % (breadth - 1)) % (breadth - 1), :]
        )
        y = tf.concat([y, flat_pad], axis=-2)

        # "slide" columns to diagonals through reshape
        y = tf.reshape(y, (group, number_heads, -1, breadth - 1, deepness))

        # slice needed "diagonal" matrix
        y = y[:, :, :-1, -lens:, :]

        if x_dimension == 4:
            # remove fake depth dimension
            y = tf.squeeze(y, axis=-1)

        return y

    def matmul_with_relative_keys(self, x: tf.Tensor) -> tf.Tensor:
        z = self.key_relative_embeddings

        if self.heads_share_relative_embedding:
            matmul = tf.einsum("bhld,md->bhlm", x, z)
        else:
            matmul = tf.einsum("bhld,hmd->bhlm", x, z)

        return self.relative_to_absolute_pos(matmul)

    def _embeddings_related_tile(self, y: tf.Tensor, length: tf.Tensor) -> tf.Tensor:
        if self.heads_share_relative_embedding:
            y = tf.expand_dims(y, axis=0)  # add head dimension

        y = tf.expand_dims(y, axis=1)  # add length dimension
        y = tf.tile(y, (1, length, 1, 1))
        return tf.expand_dims(y, axis=0)  # add batch dimension

    def _squeeze_relative_embeddings(self, y: tf.Tensor) -> tf.Tensor:
        y = tf.squeeze(y, axis=0)  # squeeze batch dimension
        if self.heads_share_relative_embedding:
            y = tf.squeeze(y, axis=1)  # squeeze head dimension
        return y

    def matmul_with_relative_vals(self, x: tf.Tensor) -> tf.Tensor:
        z = self._embeddings_related_tile(
            self.value_relative_embeddings, tf.shape(x)[-2]
        )
        z = self.relative_to_absolute_pos(z)
        z = self._squeeze_relative_embeddings(z)

        if self.heads_share_relative_embedding:
            return tf.einsum("bhlm,lmd->bhld", x, z)
        else:
            return tf.einsum("bhlm,hlmd->bhld", x, z)

    def drop_attn_logits(
        self, logits: tf.Tensor, pad_mask: tf.Tensor, training: tf.Tensor
    ) -> tf.Tensor:
        def droped_logits() -> tf.Tensor:
            keep_probability = tf.random.uniform(tf.shape(logits), 0, 1) + pad_mask
            mask_drop = tf.cast(
                tf.less(keep_probability, self.attention_dropout_rate), logits.dtype
            )

            return logits + mask_drop * -1e9

        return tf_utils.smart_cond(training, droped_logits, lambda: tf.identity(logits))

    def scaled_dot_product_attn(
        self,
        query: tf.Tensor,
        key: tf.Tensor,
        value: tf.Tensor,
        pad_mask: tf.Tensor,
        training: tf.Tensor,
    ) -> Tuple[tf.Tensor, tf.Tensor]:
        """Calculate the attention weights.

        query, key, value must have matching leading dimensions.
        key, value must have matching penultimate dimension,
        i.e.: seq_len_k = seq_len_v.
        The mask has different shapes depending on its type (padding or look ahead)
        but it must be broadcastable for addition.

        Arguments:
            query: A tensor with shape (..., length, depth).
            key: A tensor with shape (..., length, depth).
            value: A tensor with shape (..., length, depth).
            pad_mask: Float tensor with shape broadcastable
                to (..., length, length). Defaults to None.

        Returns:
            output: A tensor with shape (..., length, depth).
            attention_weights: A tensor with shape (..., length, length).
        """

        qk_matmul = tf.matmul(query, key, transpose_b=True)  # (..., length, length)

        if self.use_key_relative_position:
            qk_matmul += self.matmul_with_relative_keys(query)

        # scale matmul_qk
        dk = tf.cast(tf.shape(key)[-1], tf.float32)
        logits = qk_matmul / tf.math.sqrt(dk)

        # add the mask to the scaled tensor.
        if pad_mask is not None:
            logits += pad_mask * -1e9

        # apply attention dropout before softmax to maintain attention_weights norm as 1
        if self.attention_dropout_rate > 0:
            logits = self.drop_attn_logits(logits, pad_mask, training)

        # softmax is normalized on the last axis (length) so that the scores
        # add up to 1.
        attn_weights = tf.nn.softmax(logits, axis=-1)  # (..., length, length)

        out = tf.matmul(attn_weights, value)  # (..., length, depth)
        if self.use_value_relative_position:
            out += self.matmul_with_relative_vals(attn_weights)

        return out, attn_weights

    def splitting_heads(self, y: tf.Tensor) -> tf.Tensor:
        """Split the last dimension into (num_heads, depth).

        Transpose the result such that the shape is
        (batch_size, num_heads, length, depth)
        """

        y = tf.reshape(y, (tf.shape(y)[0], -1, self.num_heads, self._depth))
        return tf.transpose(y, perm=[0, 2, 1, 3])

    def combining_heads(self, y: tf.Tensor) -> tf.Tensor:
        """Inverse of split_heads.

        Args:
            y: A Tensor with shape [batch, num_heads, length, units / num_heads]

        Returns:
            A Tensor with shape [batch, length, units]
        """

        # (batch_size, length, num_heads, depth)
        y = tf.transpose(y, perm=[0, 2, 1, 3])
        # (batch_size, length, units)
        return tf.reshape(y, (tf.shape(y)[0], -1, self.units))

    # noinspection PyMethodOverriding
    def call(
        self,
        query_input: tf.Tensor,
        source_input: tf.Tensor,
        pad_mask: Optional[tf.Tensor] = None,
        train: Optional[Union[tf.Tensor, bool]] = None,
    ) -> Tuple[tf.Tensor, tf.Tensor]:
        """Apply attention mechanism to query_input and source_input.

        Arguments:
            query_input: A tensor with shape [batch_size, length, input_size].
            source_input: A tensor with shape [batch_size, length, input_size].
            pad_mask: Float tensor with shape broadcastable
                to (..., length, length). Defaults to None.
            train: A bool, whether in training mode or not.

        Returns:
            Attention layer output with shape [batch_size, length, units]
        """
        if train is None:
            train = K.learning_phase()

        query_data = self._query_dense_layer(query_input)  # (batch_size, length, units)
        key_value = self._key_dense_layer(source_input)  # (batch_size, length, units)
        fetch_value = self._value_dense_layer(source_input)  # (batch_size, length, units)

        query_data = self.splitting_heads(query_data)  # (batch_size, num_heads, length, depth)
        key_value = self.splitting_heads(key_value)  # (batch_size, num_heads, length, depth)
        fetch_value = self.splitting_heads(fetch_value)  # (batch_size, num_heads, length, depth)

        attn, attn_weighs = self.scaled_dot_product_attn(
            query_data, key_value, fetch_value, pad_mask, train
        )
        # attention.shape == (batch_size, num_heads, length, depth)
        # attention_weights.shape == (batch_size, num_heads, length, length)
        attn = self.combining_heads(attn)  # (batch_size, length, units)

        out = self._output_dense_layer(attn)  # (batch_size, length, units)

        return out, attn_weighs


class ConverterEncoderLayer(tf.keras.layers.Layer):
    """Transformer encoder layer.

    The layer is composed of the sublayers:
        1. Self-attention layer
        2. Feed-forward network (which is 2 fully-connected layers)

    Arguments:
        units: Positive integer, output dim of hidden layer.
        num_heads: Positive integer, number of heads
            to repeat the same attention structure.
        filter_units: Positive integer, output dim of the first ffn hidden layer.
        dropout_rate: Float between 0 and 1; fraction of the input units to drop.
        attention_dropout_rate: Float, dropout rate inside attention for training.
        sparsity: Float between 0 and 1. Fraction of the `kernel`
            weights to set to zero.
        unidirectional: Boolean, use a unidirectional or bidirectional encoder.
        use_key_relative_position: Boolean, if 'True' use key
            relative embeddings in attention.
        use_value_relative_position: Boolean, if 'True' use value
            relative embeddings in attention.
        max_relative_position: Positive integer, max position for relative embeddings.
        heads_share_relative_embedding: Boolean, if 'True'
            heads will share relative embeddings.
    """

    def __init__(
        self,
        units: int,
        num_heads: int,
        filter_units: int,
        dropout_rate: float = 0.1,
        attention_dropout_rate: float = 0.0,
        sparsity: float = 0.8,
        unidirectional: bool = False,
        use_key_relative_position: bool = False,
        use_value_relative_position: bool = False,
        max_relative_position: Optional[int] = None,
        heads_share_relative_embedding: bool = False,
    ) -> None:
        super().__init__()

        self._layer_norm = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self._mha = ManyHeadAttention(
            units,
            num_heads,
            attention_dropout_rate,
            sparsity,
            unidirectional,
            use_key_relative_position,
            use_value_relative_position,
            max_relative_position,
            heads_share_relative_embedding,
        )
        self._dropout = tf.keras.layers.Dropout(dropout_rate)

        self._ffn_layers = [
            tf.keras.layers.LayerNormalization(epsilon=1e-6),
            CondenseWithSparseWeights(
                units=filter_units, activation=tfa.activations.gelu, sparsity=sparsity
            ),  # (batch_size, length, filter_units)
            tf.keras.layers.Dropout(dropout_rate),
            CondenseWithSparseWeights(
                units=units, sparsity=sparsity
            ),  # (batch_size, length, units)
            tf.keras.layers.Dropout(dropout_rate),
        ]

    def call(
        self,
        y: tf.Tensor,
        pad_mask: Optional[tf.Tensor] = None,
        train: Optional[Union[tf.Tensor, bool]] = None,
    ) -> tf.Tensor:
        """Apply transformer encoder layer.

        Arguments:
            y: A tensor with shape [batch_size, length, units].
            pad_mask: Float tensor with shape broadcastable
                to (..., length, length). Defaults to None.
            train: A bool, whether in training mode or not.

        Returns:
            Transformer encoder layer output with shape [batch_size, length, units]
        """
        if train is None:
            train = K.learning_phase()

        x_normal = self._layer_norm(y)  # (batch_size, length, units)
        attention_output, _ = self._mha(x_normal, x_normal, pad_mask=pad_mask, training=train)
        attention_output = self._dropout(attention_output, training=train)
        y += attention_output

        ffn_output = y  # (batch_size, length, units)
        for layer in self._ffn_layers:
            ffn_output = layer(ffn_output, training=train)
        y += ffn_output

        return y  # (batch_size, length, units)


class ConverterEncoder(tf.keras.layers.Layer):
    """Transformer encoder.

    Encoder stack is made up of `num_layers` identical encoder layers.

    Arguments:
        num_layers: Positive integer, number of encoder layers.
        units: Positive integer, output dim of hidden layer.
        num_heads: Positive integer, number of heads
            to repeat the same attention structure.
        filter_units: Positive integer, output dim of the first ffn hidden layer.
        reg_lambda: Float, regularization factor.
        dropout_rate: Float between 0 and 1; fraction of the input units to drop.
        attention_dropout_rate: Float, dropout rate inside attention for training.
        sparsity: Float between 0 and 1. Fraction of the `kernel`
            weights to set to zero.
        unidirectional: Boolean, use a unidirectional or bidirectional encoder.
        use_key_relative_position: Boolean, if 'True' use key
            relative embeddings in attention.
        use_value_relative_position: Boolean, if 'True' use value
            relative embeddings in attention.
        max_relative_position: Positive integer, max position for relative embeddings.
        heads_share_relative_embedding: Boolean, if 'True'
            heads will share relative embeddings.
        name: Optional name of the layer.
    """

    def __init__(
        self,
        num_layers: int,
        units: int,
        num_heads: int,
        filter_units: int,
        reg_lambda: float,
        dropout_rate: float = 0.1,
        attention_dropout_rate: float = 0.0,
        sparsity: float = 0.8,
        unidirectional: bool = False,
        use_key_relative_position: bool = False,
        use_value_relative_position: bool = False,
        max_relative_position: Optional[int] = None,
        heads_share_relative_embedding: bool = False,
        name: Optional[Text] = None,
    ) -> None:
        super().__init__(name=name)

        self.units = units
        self.unidirectional = unidirectional

        regularizer_l2 = tf.keras.regularizers.l2(reg_lambda)
        self._embedding = CondenseWithSparseWeights(
            units=units, kernel_regularizer=regularizer_l2, sparsity=sparsity
        )
        # positional encoding helpers
        self._angles = self.fetch_angles()
        self._even_indices = np.arange(0, self.units, 2, dtype=np.int32)[:, np.newaxis]
        self._odd_indices = np.arange(1, self.units, 2, dtype=np.int32)[:, np.newaxis]

        self._dropout = tf.keras.layers.Dropout(dropout_rate)

        self._enc_layers = [
            ConverterEncoderLayer(
                units,
                num_heads,
                filter_units,
                dropout_rate,
                attention_dropout_rate,
                sparsity,
                unidirectional,
                use_key_relative_position,
                use_value_relative_position,
                max_relative_position,
                heads_share_relative_embedding,
            )
            for _ in range(num_layers)
        ]
        self._layer_norm = tf.keras.layers.LayerNormalization(epsilon=1e-6)

    def fetch_angles(self) -> np.ndarray:
        k = np.arange(self.units)[np.newaxis, :]
        return 1 / np.power(10000, (2 * (k // 2)) / np.float32(self.units))

    def encoding_positional(self, maximum_position: tf.Tensor) -> tf.Tensor:
        maximum_position = tf.cast(maximum_position, dtype=tf.float32)
        angle_radius = tf.range(maximum_position)[:, tf.newaxis] * self._angles

        # transpose for easy slicing
        angle_radius = tf.transpose(angle_radius, perm=[1, 0])
        structures = tf.shape(angle_radius)
        # apply sin to even indices in the array; 2i
        even_sin = tf.sin(tf.gather_nd(angle_radius, self._even_indices))
        even_pos_encoding = tf.scatter_nd(self._even_indices, even_sin, structures)
        # apply cos to odd indices in the array; 2i+1
        odd_cos = tf.cos(tf.gather_nd(angle_radius, self._odd_indices))
        odd_pos_encoding = tf.scatter_nd(self._odd_indices, odd_cos, structures)
        # combine even and odd positions and transpose back
        encoding_pos = tf.transpose(even_pos_encoding + odd_pos_encoding, perm=[1, 0])
        # add batch dimension
        return tf.stop_gradient(encoding_pos[tf.newaxis, ...])

    @staticmethod
    def look_ahead_padding_mask(max_position: tf.Tensor) -> tf.Tensor:
        padding_mask = 1 - tf.linalg.band_part(tf.ones((max_position, max_position)), -1, 0)
        return padding_mask[tf.newaxis, tf.newaxis, :, :]  # (1, 1, seq_len, seq_len)

    def call(
        self,
        y: tf.Tensor,
        padding_mask: Optional[tf.Tensor] = None,
        training: Optional[Union[tf.Tensor, bool]] = None,
    ) -> tf.Tensor:
        """Apply transformer encoder.

        Arguments:
            y: A tensor with shape [batch_size, length, input_size].
            padding_mask: Float tensor with shape broadcastable
                to (..., length, length). Defaults to None.
            training: A bool, whether in training mode or not.

        Returns:
            Transformer encoder output with shape [batch_size, length, units]
        """

        # adding embedding and position encoding.
        y = self._embedding(y)  # (batch_size, length, units)
        y *= tf.math.sqrt(tf.cast(self.units, tf.float32))
        y += self.encoding_positional(tf.shape(y)[1])
        y = self._dropout(y, training=training)

        if padding_mask is not None:
            padding_mask = tf.squeeze(padding_mask, -1)  # (batch_size, length)
            padding_mask = padding_mask[:, tf.newaxis, tf.newaxis, :]
            # pad_mask.shape = (batch_size, 1, 1, length)
            if self.unidirectional:
                # add look ahead pad mask to emulate unidirectional behavior
                padding_mask = tf.minimum(
                    1.0, padding_mask + self.look_ahead_padding_mask(tf.shape(padding_mask)[-1])
                )  # (batch_size, 1, length, length)

        for layer in self._enc_layers:
            y = layer(y, pad_mask=padding_mask, training=training)

        # if normalization is done in encoding layers, then it should also be done
        # on the output, since the output can grow very large, being the sum of
        # a whole stack of unnormalized layer outputs.
        return self._layer_norm(y)  # (batch_size, length, units)
