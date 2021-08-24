"""[summary]

This model is quite similar to mscalev3.py
but I've implemented a change to the architecture.

In each of the sub-networks there are blocks of layers.
At the end of each block there is a branched "output" layer.
It is not an actual output of the network though.
Instead it is a residual node, at the end of the block we sum up
all these branched "output" nodes to give the output prediction
from each sub-network.

In addition, each block also has a skip-connection.

Then each output from the sub-networks are themselves summed up to produce
the final output prediction.

The reasoning is that this produces a residual connection that is
easier to understand in the regression sense.

"""

import tensorflow as tf
import tensorflow_addons as tfa
from wispy.mscalev3 import make_scale_tensor, ScaleLayer

# this version supports variable number of units and blocks for each scale.
# the idea is that maybe smaller scales can cope with smaller networks
def build_model(
    input_shape=1,
    output_shape=1,
    units=128,
    activation="relu",
    n_blocks=2,
    scales=[1],
    layers_per_block=3,
    scale_activation="relu",
    scale_dimension=0,
    dtype=None,
):
    """[summary]

    Args:
        input_shape (int, optional): [description]. Defaults to 1.
        output_shape (int, optional): [description]. Defaults to 1.
        units (int, optional): [description]. Defaults to 128.
        activation (str, optional): [description]. Defaults to "relu".
            The activation function to use in the rest of the network
        n_blocks (int, optional): [description]. Defaults to 2.
        scales (list, optional): [description]. Defaults to [1].
        layers_per_block (int, optional): [description]. Defaults to 3.
        scale_activation (str, optional): [description]. Defaults to "relu".
            The activation function to use after the ScaleLayer, Dense Layers
        scale_dimension (int, optional): [description]. Defaults to 0.
            Use this to select which feature to apply the scaling to.
        dtype ([type], optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """
    input_layer = tf.keras.Input(shape=(input_shape,))

    outputs = [None] * len(scales)

    for i, scale in enumerate(scales):
        scale_tensor = make_scale_tensor(
            input_shape, scale_dimension, scale, dtype=dtype
        )
        scaled_input = ScaleLayer(scale_tensor)(input_layer)

        x = tf.keras.layers.Dense(units, activation=scale_activation)(scaled_input)
        # x = tf.keras.layers.Activation(scale_activation)(x)

        outputs[i] = []

        for k in range(n_blocks):
            tmp = x
            for j in range(layers_per_block):
                x = tf.keras.layers.Dense(units, activation=activation)(x)
                # x = tf.keras.layers.Activation(activation)(x)
            # x = tfa.layers.GroupNormalization(groups=1)(x)
            x = tf.keras.layers.add([x, tmp])
            outputs[i].append(tf.keras.layers.Dense(output_shape)(x))
        outputs[i] = tf.keras.layers.add([output for output in outputs[i]])

    if len(outputs) > 1:
        outputs = tf.keras.layers.add([output for output in outputs])
    else:
        outputs = outputs[0]

    model = tf.keras.models.Model(inputs=input_layer, outputs=outputs)

    return model