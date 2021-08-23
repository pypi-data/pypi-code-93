# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#      https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
"""Argument and result types for nodes."""

# pylint:disable=too-few-public-methods


class Target:
    """
    A target gate for an infidelity calculation.

    Attributes
    ----------
    value_shape : tuple
        The shape of the target gate operation.

    See Also
    --------
    target : Define the target operation of a time evolution.
    """


class Tensor:
    """
    A multi-dimensional array of data.

    Most functions accepting a :obj:`.Tensor` object can alternatively accept a NumPy array.

    You can use the arithmetic operators ``+``, ``-``, ``*``, ``**``, ``/``, ``//``, and ``@``
    to perform operations between two `Tensor` objects.

    Attributes
    ----------
    shape : tuple
        The shape of the tensor.
    name : str
        The name assigned to the node.
    """


class Pwc:
    """
    A piecewise-constant tensor-valued function of time (or batch of such functions).

    You can use the arithmetic operators ``+``, ``-``, ``*``, ``**``, ``/``, ``//``, and ``@``
    to perform operations between two `Pwc` objects or between a `Pwc` and a `Tensor`.

    Attributes
    ----------
    values : Tensor
        The values of the function on the piecewise-constant segments.
    durations : np.ndarray
        The durations of the constant segments.
    value_shape : tuple
        The shape of the function value.
    batch_shape : tuple
        The shape of the batch in the function.
    name : str
        The name assigned to the node.

    See Also
    --------
    pwc : Create piecewise-constant functions.
    """


class SparsePwc:
    """
    A piecewise-constant sparse-matrix-valued function of time.

    Attributes
    ----------
    value_shape : tuple
        The shape of the function value.

    See Also
    --------
    sparse_pwc_operator : Create `SparsePwc` operators.
    """


class Stf:
    """
    A sampleable tensor-valued function of time (or batch of such functions).

    You can use the arithmetic operators ``+``, ``-``, ``*``, ``**``, ``/``, ``//``, and ``@``
    to perform operations between two `Stf` objects or between an `Stf` and a `Tensor`.

    Attributes
    ----------
    value_shape : tuple
        The shape of the function value.
    batch_shape : tuple
        The shape of the batch in the function.

    Notes
    -----
    Stf represents an arbitrary function of time. Piecewise-constant (PWC) or constant functions
    are special cases of Stfs and Q-CTRL python package provides specific APIs to support them.
    Note that as the PWC property can simplify the calculation, you should always consider using
    PWC-related APIs if your system parameters or controls are described by PWC functions.

    See Also
    --------
    identity_stf : Create an `Stf` representing the identity function.
    """


class ConvolutionKernel:
    """
    A kernel to be used in a convolution.

    See Also
    --------
    convolve_pwc : Create an `Stf` by convolving a `Pwc` with a kernel.
    gaussian_convolution_kernel : Create a convolution kernel representing a normalized Gaussian.
    sinc_convolution_kernel : Create a convolution kernel representing the sinc function.
    """


# Registry of all types created by operations.
TYPE_REGISTRY = [
    Target,
    Tensor,
    Pwc,
    SparsePwc,
    Stf,
    ConvolutionKernel,
]
