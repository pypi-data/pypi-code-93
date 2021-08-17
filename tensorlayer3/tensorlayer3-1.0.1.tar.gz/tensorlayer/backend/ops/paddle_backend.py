#! /usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
import paddle as pd
import paddle.nn as nn
import numpy as np
import paddle.nn.functional as F
from .paddle_nn import nchw_to_nhwc, nhwc_to_nchw, preprocess_2d_format

_dtypeDict = ["float16", "float32", "float64", "int8", "int16", "int32", "int64", "uint8", "uint16", "uint32", "uint64"]
# TODO NotImplemented
DType = None
float16 = "float16"
float32 = "float32"
float64 = "float64"
int8 = "int8"
int16 = "int16"
int32 = "int32"
int64 = "int64"
uint8 = "uint8"
uint16 = "uint16"
uint32 = "uint32"
uint64 = "uint64"


def _getter(init_fn, **kwargs):
    """Return an named eager tensor."""
    raise NotImplementedError


def set_context(**kwargs):
    raise Exception("Using Paddle backend,You don't need to set context")


def get_tensor_shape(x):
    return pd.shape(x)


# initializers
def zeros(shape, dtype="float32"):
    """
    Creates a tensor with all elements set to zero.

    Parameters
    ----------
    shape : A list of integers
        a tuple of integers, or a 1-D Tensor of type int32.
    dtype : tensor
        The DType of an element in the resulting Tensor

    Returns
    -------
        A Tensor with all elements set to zero.

    """
    return pd.zeros(shape=shape, dtype=dtype)


def ones(shape, dtype="float32"):
    """
    Creates a tensor with all elements set to ones.

    Parameters
    ----------
    shape : A list of integers
        a tuple of integers, or a 1-D Tensor of type int32.
    dtype : tensor
        The DType of an element in the resulting Tensor

    Returns
    -------
        A Tensor with all elements set to zero.

    """
    return pd.ones(shape=shape, dtype=dtype)


def constant(value, shape, dtype="float32"):
    """
    Creates a constant tensor from a tensor-like object.

    Parameters
    ----------
    value : list
        A constant value (or list) of output type dtype.
    dtype : tensor
         The type of the elements of the resulting tensor.
    shape : tuple
        Optional dimensions of resulting tensor.

    Returns
    -------
        A Constant Tensor.

    """
    return nn.initializer.constant(value=value)


def random_uniform(shape, minval=0, maxval=None, dtype="float32", seed=None):
    """
    Outputs random values from a uniform distribution.

    Parameters
    ----------
    shape : tuple
        A 1-D integer Tensor or Python array. The shape of the output tensor.
    minval : int
        The lower bound on the range of random values to generate (inclusive). Defaults to 0.
    maxval : int
        The upper bound on the range of random values to generate (exclusive). Defaults to 1 if dtype is floating point.
    dtype : tensor
        The type of the output: float16, float32, float64, int32, or int64.
    seed : int
         Used in combination with dragon.random.set_seed to create a reproducible sequence of tensors across multiple calls.
    Returns
    -------
        A tensor of the specified shape filled with random uniform values.

    """
    raise NotImplementedError


def random_normal(shape, mean=0.0, stddev=1.0, dtype="float32", seed=None):
    """
    Outputs random values from a normal distribution.

    Parameters
    ----------
    shape : tuple
        A 1-D integer Tensor or Python array. The shape of the output tensor.
    mean : float
        The mean of the normal distribution
    stddev : float
        The standard deviation of the normal distribution.
    dtype : tensor
        The type of the output.
    seed : A Python integer
         Used to create a random seed for the distribution

    Returns
    -------
        A tensor of the specified shape filled with random normal values.

    """
    return pd.normal(mean, stddev, shape)


def truncated_normal(shape, mean=0.0, stddev=1.0, dtype="float32", seed=None):
    """
    Outputs random values from a truncated normal distribution.

    Parameters
    ----------
    shape : tuple
        A 1-D integer Tensor or Python array. The shape of the output tensor.
    mean : float
        The mean of the normal distribution
    stddev : float
        The standard deviation of the normal distribution.
    dtype : tensor
        The type of the output.
    seed : A Python integer
         Used to create a random seed for the distribution

    Returns
    -------
        A tensor of the specified shape filled with random truncated normal values.

    """
    raise NotImplementedError


def he_normal(shape, dtype, seed=None):
    """
    He normal initializer.

    Parameters
    ----------
    seed : A Python integer.
        Used to seed the random generator.
    shape : tuple
        A 1-D integer Tensor or Python array. The shape of the output tensor.
    dtype : tensor
        The type of the output.

    Returns
    -------
        A tensor of the specified shape filled with he normal values.
    """
    # shape = shape[::-1]
    raise NotImplementedError

def xavier_normal(shape, dtype, seed=None):
    """
    xavier normal initializer.

    Parameters
    ----------
    seed : A Python integer.
        Used to seed the random generator.
    shape : tuple
        A 1-D integer Tensor or Python array. The shape of the output tensor.
    dtype : tensor
        The type of the output.

    Returns
    -------
        A tensor of the specified shape filled with xavier normal values.
    """

    raise NotImplementedError

def xavier_uniform(shape, dtype, seed=None):
    """
    xavier uniform initializer.

    Parameters
    ----------
    seed : A Python integer.
        Used to seed the random generator.
    shape : tuple
        A 1-D integer Tensor or Python array. The shape of the output tensor.
    dtype : tensor
        The type of the output.

    Returns
    -------
        A tensor of the specified shape filled with xavier uniform values.
    """

    raise NotImplementedError


def Variable(initial_value, name, trainable=None):
    """
    Creates a new variable with value initial_value.

    Parameters
    ----------
    initial_value : tensor
        A Tensor, or Python object convertible to a Tensor
    name : str
        Optional name for the variable. Defaults to 'Variable' and gets uniquified automatically.
    Returns
    -------
        Variable
    """
    raise NotImplementedError


class MatMul(object):

    def __init__(self):
        pass

    def __call__(self, a, b):
        return pd.matmul(x=a, y=b)


def matmul(a, b):
    """
    Multiplies matrix a by matrix b, producing a * b.

    Parameters
    ----------
    a : tensor
         type float16, float32, float64, int32, complex64, complex128 and rank > 1.
    b : tensor
        with same type and rank as a.

    Returns
    -------
        A Tensor of the same type as a and b
    """
    raise NotImplementedError


def add(value, bias):
    """
    Returns x + y element-wise.

    Parameters
    ----------
    value :  tensor.
        Must be one of the following types: bfloat16, half, float32, float64,
        uint8, int8, int16, int32, int64, complex64, complex128, string.
    bias : tensor
        Must have the same type as a
    name : str
        A name for the operation

    Returns
    -------
        A Tensor. Has the same type as a.
    """

    raise NotImplementedError


def dtypes(dt):
    """
    Data dtypes.

    Parameters
    ----------
    dt : string
         It could be 'uint8', 'uint16', 'uint32', 'uint64', 'int8', 'int16',
         'int32', 'int64', 'float16', 'float32', 'float64', 'DType'.

    Returns
    -------
        Data dtypes
    """
    raise NotImplementedError


class Maximum(object):

    def __init__(self):
        pass

    def __call__(self, x, y):
        raise NotImplementedError


class Minimum(object):

    def __init__(self):
        pass

    def __call__(self, x, y):
        raise NotImplementedError


def minimum(x, y):
    """
    Returns the min of x and y (i.e. x < y ? x : y) element-wise.

    Parameters
    ----------
    x : tensor.
        Must be one of the following types: bfloat16, half, float32, float64, int32, int64.
    y : A Tensor.
        Must have the same type as x.
    name : str
        A name for the operation (optional).

    Returns
    -------
        A Tensor. Has the same type as x
    """
    raise NotImplementedError


class FlattenReshape(object):

    def __init__(self):
        pass

    def __call__(self, inputs):
        return pd.flatten(x=inputs, start_axis=1, stop_axis=-1)


class Reshape(object):

    def __init__(self, shape):
        self.shape = shape

    def __call__(self, tensor):
        return pd.reshape(tensor, shape=self.shape)


def reshape(tensor, shape):
    """
    Reshapes a tensor.

    Parameters
    ----------
    tensor : tensor
        A Tensor.
    shape : tensor
         Defines the shape of the output tensor.
    Returns
    -------
        A Tensor. Has the same type as tensor
    """
    return pd.reshape(tensor, shape)


class Concat(object):

    def __init__(self, axis):
        super(Concat, self).__init__()
        self.axis = axis

    def __call__(self, values):
        return pd.concat(values, axis=self.axis)


def concat(values, axis):
    """
    Concatenates tensors along one dimension.

    Parameters
    ----------
    values : list
         A list of Tensor objects or a single Tensor
    axis : int
        0-D int32 Tensor. Dimension along which to concatenate
    Returns
    -------
        A Tensor resulting from concatenation of the input tensors.
    """
    return pd.concat(values, axis)


def convert_to_tensor(value, dtype=float32):
    """
    Converts the given value to a Tensor.

    Parameters
    ----------
    value : object
        An object whose type has a registered Tensor conversion function.
    dtype : optional
        Optional element type for the returned tensor. If missing, the type is inferred from the type of value.

    Returns
    -------
        A Tensor based on value.
    """
    return pd.to_tensor(value, dtype=dtype)


def convert_to_numpy(value):
    return value.numpy()


def sqrt(x):
    """
    Computes square root of x element-wise.

    Parameters
    ----------
    x : tensor
         Must be one of the following types: bfloat16, half, float32, float64, complex64, complex128.

    Returns
    -------
        A Tensor. Has the same type as x.
    """
    return pd.sqrt(x)


class ReduceSum(object):

    def __init__(self, axis):
        self.axis = axis

    def construct(self, input):
        return pd.sum(input, axis=self.axis)


class ReduceMean(object):

    def __init__(self, axis):
        self.axis = axis

    def __call__(self, inputs):
        return pd.mean(inputs, axis=self.axis)


def reduce_mean(input_tensor, axis=None):
    """
    Computes the mean of elements across dimensions of a tensor.

    Parameters
    ----------
    input_tensor : tensor
        The tensor to reduce. Should have numeric type.
    axis : int
        The dimensions to reduce. If None (the default), reduces all dimensions.
        Must be in the range [-rank(input_tensor), rank(input_tensor)).
    name : str
        A name for the operation (optional).

    Returns
    -------
        The reduced tensor.
    """

    return pd.mean(input_tensor, axis)


class ReduceMax(object):

    def __init__(self, axis):
        self.axis = axis

    def __call__(self, inputs):
        return pd.max(inputs, axis=self.axis)


def reduce_max(input_tensor, axis=None):
    """
    Computes the maximum of elements across dimensions of a tensor.

    Parameters
    ----------
    input_tensor : tensor
        The tensor to reduce. Should have real numeric type.
    axis : int
        The dimensions to reduce. If None (the default), reduces all dimensions.
        Must be in the range [-rank(input_tensor), rank(input_tensor)).
    name : str
        A name for the operation (optional).

    Returns
    -------
        The reduced tensor.
    """

    return pd.max(input_tensor, axis)


def reduce_min(input_tensor, axis=None):
    """
    Computes the minimum of elements across dimensions of a tensor.

    Parameters
    ----------
    input_tensor : tensor
        The tensor to reduce. Should have real numeric type.
    axis : int
        The dimensions to reduce. If None (the default), reduces all dimensions.
        Must be in the range [-rank(input_tensor), rank(input_tensor)).
    name : str
        A name for the operation (optional).

    Returns
    -------
        The reduced tensor.
    """
    return pd.min(input_tensor, axis)


class Pad(object):

    def __init__(self, paddings, mode="REFLECT", constant_values=0):
        if mode not in ['CONSTANT', 'REFLECT', 'SYMMETRIC']:
            raise Exception("Unsupported mode: {}".format(mode))
        if mode == 'SYMMETRIC':
            raise NotImplementedError
        self.paddings = paddings
        self.mode = mode.lower()
        self.constant_values = constant_values

    def __call__(self, x):
        if len(x.shape) == 3:
            data_format = 'NLC'
            self.paddings = self.correct_paddings(len(x.shape), self.paddings, data_format)
        elif len(x.shape) == 4:
            data_format = 'NHWC'
            self.paddings = self.correct_paddings(len(x.shape), self.paddings, data_format)
        elif len(x.shape) == 5:
            data_format = 'NDHWC'
            self.paddings = self.correct_paddings(len(x.shape), self.paddings, data_format)
        else:
            raise NotImplementedError('Please check the input shape.')
        return pd.nn.functional.pad(x, self.paddings, self.mode, value=self.constant_values, data_format=data_format)

    def correct_paddings(self, in_shape, paddings, data_format):
        if in_shape == 3 and data_format == 'NLC':
            correct_output = [paddings[1][0], paddings[1][1]]
        elif in_shape == 4 and data_format == 'NHWC':
            correct_output = [paddings[2][0], paddings[2][1], paddings[1][0], paddings[1][1]]
        elif in_shape == 5 and data_format == 'NDHWC':
            correct_output = [
                paddings[3][0], paddings[3][1], paddings[2][0], paddings[2][1], paddings[1][0], paddings[1][1]
            ]
        else:
            raise NotImplementedError('Does not support channels first')
        return correct_output


def pad(tensor, paddings, mode='CONSTANT', constant_values=0):
    """
    Pads a tensor.

    Parameters
    ----------
    tensor : tensor
        A Tensor.
    paddings : tuple
        A tuple of type int32.
    mode : str
        One of "CONSTANT", "REFLECT", or "SYMMETRIC" (case-insensitive)
    constant_values : int
        In "CONSTANT" mode, the scalar pad value to use. Must be same type as tensor.

    Returns
    -------
        A Tensor. Has the same type as tensor.
    """
    return Pad(paddings, mode, constant_values)(tensor)


class Unstack(object):

    def __init__(self, axis, num=None):
        self.axis = axis
        self.num = num

    def __call__(self, values):
        return pd.unstack(values, self.axis, self.num)


class Stack(object):

    def __init__(self, axis):
        self.axis = axis

    def __call__(self, values):
        return pd.stack(values, self.axis)


def stack(values, axis=0):
    """
    Stacks a list of rank-R tensors into one rank-(R+1) tensor.

    Parameters
    ----------
    values : list or tuple
        A list of Tensor objects with the same shape and type.
    axis : int
        An int. The axis to stack along. Defaults to the first dimension.
        Negative values wrap around, so the valid range is [-(R+1), R+1).

    Returns
    -------
        A stacked Tensor with the same type as values.
    """
    return pd.stack(values, axis=axis)


class Meshgrid(object):

    def __init__(self, indexing='xy'):
        super(Meshgrid, self).__init__()
        self.index = indexing

    def __call__(self, inputs):
        return pd.meshgrid(inputs)


def meshgrid(*args, **kwargs):
    """
    Broadcasts parameters for evaluation on an N-D grid.

    Parameters
    ----------
    x : tensor
        Tensors with rank 1.
    y : tensor
        Tensors with rank 1.

    Returns
    -------
        A list of N Tensors with rank N.
    """

    return pd.meshgrid(*args, **kwargs)


def range(start, limit=None, delta=1, dtype=None):
    """
    Creates a sequence of numbers.

    Parameters
    ----------
    start : tensor
        A 0-D Tensor (scalar). Acts as first entry in the range if limit is not None;
        otherwise, acts as range limit and first entry defaults to 0.
    limit : tensor
         A 0-D Tensor (scalar). Upper limit of sequence, exclusive. If None,
         defaults to the value of start while the first entry of the range defaults to 0.
    delta : tensor
        A 0-D Tensor (scalar). Number that increments start. Defaults to 1.
    dtype : type
        The type of the elements of the resulting tensor.

    Returns
    -------
        An 1-D Tensor of type dtype.
    """
    return pd.arange(start, step=delta)


class ExpandDims(object):

    def __init__(self, axis):
        self.axis = axis

    def __call__(self, input):
        input = convert_to_numpy(input)
        output = np.expand_dims(input, axis=self.axis)
        output = convert_to_tensor(output)
        return output


def expand_dims(input, axis):
    """
    Inserts a dimension of 1 into a tensor's shape.

    Parameters
    ----------
    input : tensor
        A Tensor.
    axis : int
        0-D (scalar). Specifies the dimension index at which to expand the shape of input.
        Must be in the range [-rank(input) - 1, rank(input)].

    Returns
    -------
        A Tensor with the same data as input, but its shape has an additional dimension of size 1 added.
    """

    input = convert_to_numpy(input)
    output = np.expand_dims(input, axis=axis)
    output = convert_to_tensor(output)
    return output


class Tile(object):

    def __init__(self):
        pass

    def __call__(self, input, multiples):
        return pd.tile(input, multiples)


def tile(input, multiples):
    """
    Constructs a tensor by tiling a given tensor.

    Parameters
    ----------
    input : tensor
        A Tensor. 1-D or higher.
    multiples : tensor
        Must be one of the following types: int32, int64. 1-D.
        Length must be the same as the number of dimensions in input

    Returns
    -------
        A Tensor. Has the same type as input.
    """
    return pd.tile(input, multiples)


class Cast(object):

    def __init__(self, dtype):
        self.dtype = dtype

    def __call__(self, input):
        return pd.cast(input, self.dtype)


def cast(x, dtype):
    """
    Casts a tensor to a new type.

    Parameters
    ----------
    x : tensor
        A Tensor or SparseTensor or IndexedSlices of numeric type.
        It could be uint8, uint16, uint32, uint64, int8, int16, int32, int64, float16, float32, float64.
    dtype : dtpye
         The destination type. The list of supported dtypes is the same as x

    Returns
    -------
        A Tensor or SparseTensor or IndexedSlices with same shape as x and same type as dtype.
    """
    return pd.cast(x, dtype)


class Transpose(object):

    def __init__(self, perm, conjugate=False):
        self.perm = perm
        if conjugate:
            raise ("The conjugate Parameters not supported")

    def __call__(self, a):
        return pd.transpose(a, self.perm)


def transpose(a, perm=None, conjugate=False):
    """
    Transposes a.

    Parameters
    ----------
    a : tensor
        A Tensor.
    perm : int
        A permutation of the dimensions of a.
    conjugate : bool
        Setting it to True is mathematically equivalent to ms.math.conj(ms.transpose(input)).

    Returns
    -------
        A transposed Tensor.
    """

    return pd.transpose(a, perm)


def gather_nd(params, indices, batch_dims=0):
    """
    Gather slices from params into a Tensor with shape specified by indices.

    Parameters
    ----------
    params : tensor
        The tensor from which to gather values.
    indices : tensor
        Must be one of the following types: int32, int64. Index tensor.
    batch_dims : int
        An integer or a scalar 'Tensor'. The number of batch dimensions.

    Returns
    -------
        A Tensor. Has the same type as params.
    """

    return pd.gather_nd(params, indices)


def clip_by_value(t, clip_value_min, clip_value_max):
    """
    Clips tensor values to a specified min and max.

    Parameters
    ----------
    t : tensor
        A Tensor or IndexedSlices
    clip_value_min : tensor
        A 0-D (scalar) Tensor, or a Tensor with the same shape as t. The minimum value to clip by
    clip_value_max : tensor
        A 0-D (scalar) Tensor, or a Tensor with the same shape as t. The minimum value to clip by

    Returns
    -------
        A clipped Tensor or IndexedSlices.
    """

    return pd.clip(t, clip_value_min, clip_value_max)


def split(value, num_or_size_splits, axis=0, num=None):
    """
    Splits a tensor into sub tensors.

    Parameters
    ----------
    value : tensor
        The Tensor to split.
    num_or_size_splits : list or tuple
        Either an integer indicating the number of splits along split_dim or a 1-D integer Tensor or
        Python list containing the sizes of each output tensor along split_dim.
    axis : int
        The dimension along which to split. Must be in the range [-rank(value), rank(value)). Defaults to 0.
    num : int
        used to specify the number of outputs when it cannot be inferred from the shape of size_splits.

    Returns
    -------
        Tensor objects resulting from splitting value.
    """
    pd.split(value, num_or_size_splits, axis)


class Floor(object):

    def __call__(self, x):
        return pd.floor(x)


def floor(x):
    return pd.floor(x)


def gather(params, indices):
    return pd.gather(params, indices)


def linspace(start, stop, num):
    return pd.linspace(start, stop, num)


def slice(inputs, starts, sizes):
    return pd.slice(inputs, starts=starts, ends=sizes)


def add_n(inputs):
    return pd.add_n(inputs)


class OneHot(object):

    def __init__(self, axis=-1, depth=1, on_value=1.0, off_value=0.0, dtype="float32"):
        self.depth = depth
        self.dtype = dtype

    def __call__(self, indices):
        output = pd.nn.functional.one_hot(indices, self.depth)
        return output


class L2Normalize(object):

    def __init__(self, axis=None, epsilon=1e-12):
        super(L2Normalize, self).__init__()
        self.axis = axis
        self.epsilon = epsilon

    def __call__(self, input):
        return pd.nn.functional.normalize(x=input, p=2, axis=self.axis, epsilon=self.epsilon)


class EmbeddingLookup(object):

    def __init__(self, max_norm=None):
        self.max_norm = max_norm

    def __call__(self, params, ids):
        pass


class NCELoss(object):

    def __init__(self, num_true=1, sampled_values=None, remove_accidental_hits=False):
        super(NCELoss, self).__init__()

    def __call__(self, weights, biases, labels, inputs, num_sampled, num_classes):
        pass


class NotEqual(object):

    def __init__(self):
        pass

    def __call__(self, x, y):
        pass


class CountNonzero(object):

    def __init__(self, keepdims=None, dtype="int64"):
        pass

    def __call__(self, *args, **kwargs):
        pass


class Resize:

    def __init__(self, scale, method, antialias=False, data_format='channels_last'):
        if method not in ['nearest', 'linear', 'bilinear']:
            raise ('Current resize does not support this method.')
        self.method = method
        self.antialias = antialias
        self.scale = scale
        self.data_format, _ = preprocess_2d_format(data_format, None)

    def __call__(self, inputs):
        output_size = [int(inputs.shape[1] * self.scale[0]), int(inputs.shape[2] * self.scale[1])]
        out = F.interpolate(
            inputs, size=output_size, mode=self.method, data_format=self.data_format, align_corners=self.antialias
        )
        return out


def resize(inputs, output_size, method, antialias):
    return Resize(output_size, method, antialias)(inputs)


class ZeroPadding1D(object):

    def __init__(self, padding):
        padding = ((0, 0), padding, (0, 0))
        self.pad = Pad(paddings=padding)

    def __call__(self, inputs):
        return self.pad(inputs)


class ZeroPadding2D(object):

    def __init__(self, padding):
        padding = ((0, 0), padding[0], padding[1], (0, 0))
        self.pad = Pad(paddings=padding)

    def __call__(self, inputs):
        return self.pad(inputs)


class ZeroPadding3D(object):

    def __init__(self, padding):
        padding = ((0, 0), padding[0], padding[1], padding[2], (0, 0))
        self.pad = Pad(paddings=padding)

    def __call__(self, inputs):
        return self.pad(inputs)


class Sign(object):

    def __init__(self):
        pass

    def __call__(self, x):
        raise NotImplementedError


class Ceil(object):

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


def ceil(x):
    raise NotImplementedError


def multiply(x, y):
    raise NotImplementedError


def divide(x, y):
    raise NotImplementedError


def identity(x):
    raise NotImplementedError


class BatchToSpace(object):

    def __init__(self, block_size, crops):
        super(BatchToSpace, self).__init__()
        pass

    def __call__(self, input_x):
        raise NotImplementedError


class DepthToSpace(object):

    def __init__(self, block_size, data_format='NHWC'):
        pass

    def __call__(self, input):
        raise NotImplementedError
