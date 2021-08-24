"""[summary]

implementing multi-scale DNN MscaleDNN version 2

e.g. 2007.11207, 2009.12729

see https://gitlab.com/SpaceTimeKhantinuum/ml/-/blob/master/waveforms/april2021/mscale-tests/one-waveform.ipynb
"""

import tensorflow as tf

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


class ScaleLayer(tf.keras.layers.Layer):
    def __init__(self, scale, **kwargs):
        super(ScaleLayer, self).__init__()
        self.scale = scale

    def call(self, inputs):
        return inputs * self.scale

    def get_config(self):
        config = super(ScaleLayer, self).get_config()
        config.update({"scale": self.scale})
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
):
    assert (
        len(scales) == len(n_blocks) == len(units)
    ), "units, n_blocks, scales must have same length"

    input_layer = tf.keras.Input(shape=(input_shape,))

    # create sub-networks
    xs = []
    for i, scale in enumerate(scales):
        scaled_input = ScaleLayer(scale)(input_layer)
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