# based on the work by Dongwei Chen+ 2020
# "Deep Residual Learning for Nonlinear Regression"
# https://www.mdpi.com/1099-4300/22/2/193
#  https://github.com/DowellChan/ResNetRegression

# https://github.com/tiantiy/ResNetRegression/blob/master/ResNetOptimalModel.py

# modified to use GroupNormalization instead of BatchNormalization
# with groups=1 which is the same as LayerNormalization

from tensorflow.keras import layers
from tensorflow.keras import models
import tensorflow_addons as tfa


def identity_block(
    input_tensor, units, group_norm=True, groups=1, batch_norm=False, momentum=0.9
):
    """The identity block is the block that has no conv layer at shortcut.
    By default uses GroupNormalization after the Dense layer but before
    the ReLU.

    # Arguments
            input_tensor: input tensor
            units:output shape
            group_norm: bool, default True - use GroupNormalization
            groups: int, default 1 - number of groups, defaults to LayerNormalization
            batch_norm: bool, default False - use batch normalization or not
            momentum: float, default 0.9 - BatchNorm momentum parameter
    # Returns
            Output tensor for the block.
    """

    x = layers.Dense(units)(input_tensor)
    if group_norm:
        x = tfa.layers.GroupNormalization(groups=groups)(x)
    if batch_norm:
        x = layers.BatchNormalization(momentum=momentum)(x)
    x = layers.Activation("relu")(x)

    x = layers.Dense(units)(x)
    if group_norm:
        x = tfa.layers.GroupNormalization(groups=groups)(x)
    if batch_norm:
        x = layers.BatchNormalization(momentum=momentum)(x)
    x = layers.Activation("relu")(x)

    x = layers.Dense(units)(x)
    if group_norm:
        x = tfa.layers.GroupNormalization(groups=groups)(x)
    if batch_norm:
        x = layers.BatchNormalization(momentum=momentum)(x)

    x = layers.add([x, input_tensor])
    x = layers.Activation("relu")(x)

    return x


def dens_block(
    input_tensor, units, group_norm=True, groups=1, batch_norm=False, momentum=0.9
):
    """A block that has a dense layer at shortcut.
    # Arguments
            input_tensor: input tensor
            units:output shape
            group_norm: bool, default True - use GroupNormalization
            groups: int, default 1 - number of groups, defaults to LayerNormalization
            batch_norm: bool, default False - use batch normalization or not
            momentum: float, default 0.9 - BatchNorm momentum parameter
    # Returns
            Output tensor for the block.
    """
    x = layers.Dense(units)(input_tensor)
    if group_norm:
        x = tfa.layers.GroupNormalization(groups=groups)(x)
    if batch_norm:
        x = layers.BatchNormalization(momentum=momentum)(x)
    x = layers.Activation("relu")(x)

    x = layers.Dense(units)(x)
    if group_norm:
        x = tfa.layers.GroupNormalization(groups=groups)(x)
    if batch_norm:
        x = layers.BatchNormalization(momentum=momentum)(x)
    x = layers.Activation("relu")(x)

    x = layers.Dense(units)(x)
    if group_norm:
        x = tfa.layers.GroupNormalization(groups=groups)(x)
    if batch_norm:
        x = layers.BatchNormalization(momentum=momentum)(x)

    shortcut = layers.Dense(units)(input_tensor)
    if group_norm:
        shortcut = tfa.layers.GroupNormalization(groups=groups)(shortcut)
    if batch_norm:
        shortcut = layers.BatchNormalization(momentum=momentum)(shortcut)

    x = layers.add([x, shortcut])
    x = layers.Activation("relu")(x)
    return x


def ResNet(
    input_shape,
    output_shape,
    width=64,
    num_blocks=3,
    group_norm=True,
    groups=1,
    batch_norm=False,
    momentum=0.9,
):
    """builds a ResNet regression model

    By default it uses GroupNormalization with groups=1 (i.e. LayerNormalization)
    as the normalization layers.

    # Arguments
            input_shape: number of inputs
            output_shape: number of outputs
            width [64]:
            num_blocks [3]: total number of blocks. A block consists of
                            a dense block followed by two identity blocks.
            group_norm: bool, default True - use GroupNormalization
            groups: int, default 1 - number of groups, defaults to LayerNormalization
            batch_norm: bool, default False - use batch normalization or not
            momentum: float, default 0.9 - BatchNorm momentum parameter
    # Returns
            A Keras model instance.
    """
    assert num_blocks >= 1, f"num_blocks={num_blocks} not allowed. must be >= 1"

    Res_input = layers.Input(shape=(input_shape,))

    x = dens_block(Res_input, width, group_norm=group_norm, groups=groups, batch_norm=batch_norm, momentum=momentum)
    x = identity_block(x, width, group_norm=group_norm, groups=groups, batch_norm=batch_norm, momentum=momentum)
    x = identity_block(x, width, group_norm=group_norm, groups=groups, batch_norm=batch_norm, momentum=momentum)

    if num_blocks > 1:
        for i in range(1, num_blocks):
            x = dens_block(x, width, group_norm=group_norm, groups=groups, batch_norm=batch_norm, momentum=momentum)
            x = identity_block(x, width, group_norm=group_norm, groups=groups, batch_norm=batch_norm, momentum=momentum)
            x = identity_block(x, width, group_norm=group_norm, groups=groups, batch_norm=batch_norm, momentum=momentum)

    if group_norm:
        x = tfa.layers.GroupNormalization(groups=groups)(x)
    if batch_norm:
        x = layers.BatchNormalization(momentum=momentum)(x)
    x = layers.Dense(output_shape, activation="linear")(x)
    model = models.Model(inputs=Res_input, outputs=x)

    return model
