"""[summary]

implementing multi-scale DNN MscaleDNN version 2
e.g. 2007.11207, 2009.12729

But with one important difference, the scale is only applied
to the time dimension, other dimensions are left alone.

see https://gitlab.com/SpaceTimeKhantinuum/ml/-/blob/master/waveforms/july2021/time_pars_subnetwork_test/fit_multiple.ipynb
"""

import tensorflow as tf
import numpy as np

# import tensorflow_addons as tfa


def build_subnetwork(
    input_tensor, units, activation="relu", n_blocks=1, layers_per_block=3
):
    """
    subnetwork with skip-connections

    n_blocks >= 1
    """
    assert n_blocks >= 1, f"n_blocks must be >1, got {n_blocks}"

    # tmp = input_tensor
    tmp = tf.keras.layers.Dense(units, activation=activation)(input_tensor)

    x = tf.keras.layers.Dense(units, activation=activation)(input_tensor)
    # x = tfa.layers.GroupNormalization(groups=1)(x)
    # x = tf.keras.layers.BatchNormalization(momentum=0.9)(x)
    for _ in range(n_blocks):
        for _ in range(layers_per_block):
            x = tf.keras.layers.Dense(units, activation=activation)(x)
        # x = tfa.layers.GroupNormalization(groups=1)(x)
        # x = tf.keras.layers.BatchNormalization(momentum=0.9)(x)

        x = tf.keras.layers.add([x, tmp])
        tmp = x

    # single output here?
    x = tf.keras.layers.Dense(1, activation="linear")(x)

    return x


def make_scale_tensor(input_shape, scale_dimension, scale, dtype=None):
    """[summary]

    Args:
        input_shape ([type]): [description]
        scale_dimension ([type]): [description]
        scale ([type]): [description]
        dtype ([type], optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """
    scales = np.ones(shape=(input_shape,), dtype=dtype)
    scales[scale_dimension] = scale
    return scales


class ScaleLayer(tf.keras.layers.Layer):
    def __init__(self, scale_tensor, **kwargs):
        super(ScaleLayer, self).__init__()
        self.scale_tensor = scale_tensor

    def call(self, inputs):
        return tf.math.multiply(inputs, self.scale_tensor)

    def get_config(self):
        config = super(ScaleLayer, self).get_config()
        config.update({"scale_tensor": self.scale_tensor})
        return config


# this version supports variable number of units and blocks for each scale.
# the idea is that maybe smaller scales can cope with smaller networks
def build_model(
    input_shape=1,
    output_shape=1,
    units=[128],
    activation="relu",
    n_blocks=[2],
    scales=[1],
    layers_per_block=3,
    scale_dimension=0,
    dtype=None,
):
    """[summary]

    Args:
        input_shape (int, optional): [description]. Defaults to 1.
        output_shape (int, optional): [description]. Defaults to 1.
        units (list, optional): [description]. Defaults to [128].
        activation (str, optional): [description]. Defaults to "relu".
        n_blocks (list, optional): [description]. Defaults to [2].
        scales (list, optional): [description]. Defaults to [1].
        layers_per_block (int, optional): [description]. Defaults to 3.
        scale_dimension (int, optional): [description]. Defaults to 0.
            Use this to select which feature to apply the scaling to.
        dtype ([type], optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """
    assert (
        len(scales) == len(n_blocks) == len(units)
    ), "units, n_blocks, scales must have same length"

    input_layer = tf.keras.Input(shape=(input_shape,))

    # create sub-networks
    xs = []
    for i, scale in enumerate(scales):
        scale_tensor = make_scale_tensor(
            input_shape, scale_dimension, scale, dtype=dtype
        )
        scaled_input = ScaleLayer(scale_tensor)(input_layer)
        xs.append(
            build_subnetwork(
                input_tensor=scaled_input,
                units=units[i],
                activation=activation,
                n_blocks=n_blocks[i],
                layers_per_block=layers_per_block,
            )
        )

    if len(xs) > 1:
        output_layer = tf.keras.layers.add([x for x in xs])
    else:
        output_layer = xs[0]

    output_layer = tf.keras.layers.Dense(output_shape, activation="linear")(
        output_layer
    )
    model = tf.keras.models.Model(inputs=input_layer, outputs=output_layer)
    return model