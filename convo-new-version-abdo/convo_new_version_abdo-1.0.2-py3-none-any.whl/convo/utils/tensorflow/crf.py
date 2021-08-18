import tensorflow as tf

from tensorflow_addons.utils.types import TensorLike
from typeguard import typechecked
from typing import Tuple


# original code taken from
# https://github.com/tensorflow/addons/blob/master/tensorflow_addons/text/crf.py
# (modified to our neeeds)


class ConditionalRandomFieldDecodeForwardRnnCell(tf.keras.layers.AbstractRNNCell):
    """Computes the forward decoding in a linear-chain ConditionalRandomFields."""

    @typechecked
    def __init__(self, transition_params: TensorLike, **kwargs) -> None:
        """Initialize the ConditionalRandomFieldDecodeForwardRnnCell.

        Args:
          transition_params: A [num_tags, num_tags] matrix of binary
            potentials. This matrix is expanded into a
            [1, num_tags, num_tags] in preparation for the broadcast
            summation occurring within the cell.
        """
        super().__init__(**kwargs)
        self._transition_params = tf.expand_dims(transition_params, 0)
        self._num_tags = transition_params.shape[0]

    @property
    def state_size(self) -> int:
        return self._num_tags

    @property
    def output_size(self) -> int:
        return self._num_tags

    def build(self, input_shape):
        super().build(input_shape)

    def call(
        self, inputs: TensorLike, state_var: TensorLike
    ) -> Tuple[tf.Tensor, tf.Tensor]:
        """Build the ConditionalRandomFieldDecodeForwardRnnCell.

        Args:
          inputs: A [batch_size, num_tags] matrix of unary potentials.
          state_var: A [batch_size, num_tags] matrix containing the previous step's
                score values.

        Returns:
          output: A [batch_size, num_tags * 2] matrix of back_pointers and scores.
          new_state: A [batch_size, num_tags] matrix of new score values.
        """
        state_var = tf.expand_dims(state_var[0], 2)
        transformation_scores = state_var + self._transition_params
        latest_state = inputs + tf.reduce_max(transformation_scores, [1])

        back_pointers = tf.argmax(transformation_scores, 1)
        back_pointers = tf.cast(back_pointers, tf.float32)

        # apply softmax to transition_scores to get scores in range from 0 to 1
        result = tf.reduce_max(tf.nn.softmax(transformation_scores, axis=1), [1])

        # In the RNN implementation only the first value that is returned from a cell
        # is kept throughout the RNN, so that you will have the values from each time
        # step in the final output. As we need the back_pointers as well as the scores
        # for each time step, we concatenate them.
        return tf.concat([back_pointers, result], axis=1), latest_state


def conditional_random_field_decode_forward(
    inputs: TensorLike,
    state: TensorLike,
    transition_params: TensorLike,
    sequence_len: TensorLike,
) -> Tuple[tf.Tensor, tf.Tensor]:
    """Computes forward decoding in a linear-chain ConditionalRandomFields.

    Args:
      inputs: A [batch_size, num_tags] matrix of unary potentials.
      state: A [batch_size, num_tags] matrix containing the previous step's
            score values.
      transition_params: A [num_tags, num_tags] matrix of binary potentials.
      sequence_len: A [batch_size] vector of true sequence lengths.

    Returns:
      output: A [batch_size, num_tags * 2] matrix of backpointers and scores.
      new_state: A [batch_size, num_tags] matrix of new score values.
    """
    sequence_len = tf.cast(sequence_len, dtype=tf.int32)
    covered = tf.sequence_mask(sequence_len, tf.shape(inputs)[1])
    crf_forward_cell = ConditionalRandomFieldDecodeForwardRnnCell(transition_params)
    crf_forward_layer = tf.keras.layers.RNN(
        crf_forward_cell, return_sequences=True, return_state=True
    )
    return crf_forward_layer(inputs, state, mask=covered)


def crf_decoding_backward(
    back_pointers: TensorLike, result: TensorLike, state_var: TensorLike
) -> Tuple[tf.Tensor, tf.Tensor]:
    """Computes backward decoding in a linear-chain ConditionalRandomFields.

    Args:
      back_pointers: A [batch_size, num_tags] matrix of backpointer of next step
            (in time order).
      result: A [batch_size, num_tags] matrix of scores of next step (in time order).
      state_var: A [batch_size, 1] matrix of tag index of next step.

    Returns:
      new_tags: A [batch_size, num_tags] tensor containing the new tag indices.
      new_scores: A [batch_size, num_tags] tensor containing the new score values.
    """
    back_pointers = tf.transpose(back_pointers, [1, 0, 2])
    result = tf.transpose(result, [1, 0, 2])

    def _scan_fn(state: TensorLike, _inputs: TensorLike) -> tf.Tensor:
        state = tf.cast(tf.squeeze(state, axis=[1]), dtype=tf.int32)
        indexes = tf.stack([tf.range(tf.shape(_inputs)[0]), state], axis=1)
        return tf.expand_dims(tf.gather_nd(_inputs, indexes), axis=-1)

    out_tags = tf.scan(_scan_fn, back_pointers, state_var)
    # the dtype of the input parameters of tf.scan need to match
    # convert state to float32 to match the type of scores
    state_var = tf.cast(state_var, dtype=tf.float32)
    out_scores = tf.scan(_scan_fn, result, state_var)

    return tf.transpose(out_tags, [1, 0, 2]), tf.transpose(out_scores, [1, 0, 2])


def conditional_random_field_decode(
    potentials: TensorLike, transition_params: TensorLike, sequence_len: TensorLike
) -> Tuple[tf.Tensor, tf.Tensor, tf.Tensor]:
    """Decode the highest scoring sequence of tags.

    Args:
      potentials: A [batch_size, max_seq_len, num_tags] tensor of
                unary potentials.
      transition_params: A [num_tags, num_tags] matrix of
                binary potentials.
      sequence_len: A [batch_size] vector of true sequence lengths.

    Returns:
      decoding_tags: A [batch_size, max_seq_len] matrix, with dtype `tf.int32`.
                  Contains the highest scoring tag indices.
      decoding_scores: A [batch_size, max_seq_len] matrix, containing the score of
                    `decoding_tags`.
      best_score_value: A [batch_size] vector, containing the best score of `decoding_tags`.
    """
    sequence_len = tf.cast(sequence_len, dtype=tf.int32)

    # If max_seq_len is 1, we skip the algorithm and simply return the
    # argmax tag and the max activation.
    def single_sequence_func():
        decoding_tags = tf.cast(tf.argmax(potentials, axis=2), dtype=tf.int32)
        decoding_scores = tf.reduce_max(tf.nn.softmax(potentials, axis=2), axis=2)
        finest_score = tf.reshape(tf.reduce_max(potentials, axis=2), shape=[-1])
        return decoding_tags, decoding_scores, finest_score

    def multi_sequence_func():
        # Computes forward decoding. Get last score and back_pointers.
        starting_state = tf.slice(potentials, [0, 0, 0], [-1, 1, -1])
        starting_state = tf.squeeze(starting_state, axis=[1])
        input_values = tf.slice(potentials, [0, 1, 0], [-1, -1, -1])

        sequence_len_minus_one = tf.maximum(
            tf.constant(0, dtype=tf.int32), sequence_len - 1
        )

        outp, end_score = conditional_random_field_decode_forward(
            input_values, starting_state, transition_params, sequence_len_minus_one
        )

        # outp is a matrix of size [batch-size, max-seq-length, num-tags * 2]
        # split the matrix on axis 2 to get the back_pointers and scores_value, which are
        # both of size [batch-size, max-seq-length, num-tags]
        back_pointers, scores_value = tf.split(outp, 2, axis=2)

        back_pointers = tf.cast(back_pointers, dtype=tf.int32)
        back_pointers = tf.reverse_sequence(
            back_pointers, sequence_len_minus_one, seq_axis=1
        )

        scores_value = tf.reverse_sequence(scores_value, sequence_len_minus_one, seq_axis=1)

        starting_state = tf.cast(tf.argmax(end_score, axis=1), dtype=tf.int32)
        starting_state = tf.expand_dims(starting_state, axis=-1)

        initial_score = tf.reduce_max(tf.nn.softmax(end_score, axis=1), axis=[1])
        initial_score = tf.expand_dims(initial_score, axis=-1)

        tags_decode, scores_decode = crf_decoding_backward(
            back_pointers, scores_value, starting_state
        )

        tags_decode = tf.squeeze(tags_decode, axis=[2])
        tags_decode = tf.concat([starting_state, tags_decode], axis=1)
        tags_decode = tf.reverse_sequence(tags_decode, sequence_len, seq_axis=1)

        scores_decode = tf.squeeze(scores_decode, axis=[2])
        scores_decode = tf.concat([initial_score, scores_decode], axis=1)
        scores_decode = tf.reverse_sequence(scores_decode, sequence_len, seq_axis=1)

        best_score_value = tf.reduce_max(end_score, axis=1)

        return tags_decode, scores_decode, best_score_value

    if potentials.shape[1] is not None:
        # shape is statically know, so we just execute
        # the appropriate code path
        if potentials.shape[1] == 1:
            return single_sequence_func()

        return multi_sequence_func()

    return tf.cond(tf.equal(tf.shape(potentials)[1], 1), single_sequence_func, multi_sequence_func)
