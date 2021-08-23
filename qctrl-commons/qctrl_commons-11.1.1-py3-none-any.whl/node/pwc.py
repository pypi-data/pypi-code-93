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
"""Module for all the node related to PWC."""
from typing import (
    List,
    Optional,
    Union,
)

import forge
import numpy as np

from qctrlcommons.node import types
from qctrlcommons.node.base import Node
from qctrlcommons.node.deprecation import deprecated_node
from qctrlcommons.node.node_data import (
    PwcNodeData,
    TensorNodeData,
)
from qctrlcommons.node.utils import (
    validate_batch_and_value_shapes,
    validate_hamiltonian,
    validate_inputs_real_fourier_signal,
    validate_shape,
)
from qctrlcommons.preconditions import (
    check_argument,
    check_argument_integer,
    check_argument_iteratable,
    check_argument_numeric,
    check_duration,
    check_operator,
    check_sample_times,
)


class Pwc(Node):
    r"""
    Creates a piecewise-constant function of time.

    Parameters
    ----------
    durations : np.ndarray (1D, real)
        The durations :math:`\{\delta t_n\}` of the :math:`N` constant
        segments.
    values : np.ndarray or Tensor
        The values :math:`\{v_n\}` of the function on the constant segments.
        The dimension corresponding to `time_dimension` must be the same
        length as `durations`. To create a batch of
        :math:`B_1 \times \ldots \times B_n` piecewise-constant tensors of
        shape :math:`D_1 \times \ldots \times D_m`, provide this `values`
        parameter as an object of shape
        :math:`B_1\times\ldots\times B_n\times N\times D_1\times\ldots\times D_m`.
    time_dimension : int, optional
        The axis along `values` corresponding to time. All dimensions that
        come before the `time_dimension` are batch dimensions: if there are
        :math:`n` batch dimensions, then `time_dimension` is also :math:`n`.
        Defaults to 0, which corresponds to no batch. Note that you can
        pass a negative value to refer to the time dimension.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The piecewise-constant function of time :math:`v(t)`, satisfying
        :math:`v(t)=v_n` for :math:`t_{n-1}\leq t\leq t_n`, where
        :math:`t_0=0` and :math:`t_n=t_{n-1}+\delta t_n`. If you provide a
        batch of values, the returned `Pwc` represents a
        corresponding batch of :math:`B_1 \times \ldots \times B_n`
        functions :math:`v(t)`, each of shape
        :math:`D_1 \times \ldots \times D_m`.

    See Also
    --------
    pwc_operator : Create `Pwc` operators.
    pwc_signal : Create `Pwc` signals from (possibly complex) values.
    pwc_sum : Sum multiple `Pwc`\s.
    """

    name = "pwc"
    args = [
        forge.arg("durations", type=np.ndarray),
        forge.arg("values", type=Union[np.ndarray, types.Tensor]),
        forge.arg("time_dimension", type=int, default=0),
    ]

    rtype = types.Pwc

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        durations = kwargs.get("durations")
        values = kwargs.get("values")
        time_dimension = kwargs.get("time_dimension")
        check_argument_numeric(durations, "durations")
        check_argument_numeric(values, "values")
        check_argument_integer(time_dimension, "time_dimension")
        value_shape = validate_shape(values, "values")
        durations_shape = validate_shape(durations, "durations")
        check_argument(
            len(durations_shape) == 1,
            "The shape of durations must have exactly one dimension.",
            {"durations": durations},
        )
        check_argument(
            -len(value_shape) <= time_dimension < len(value_shape),
            "The `time_dimension` must be a valid `values` dimension.",
            {"time_dimension": time_dimension, "values": values},
        )
        check_argument(
            value_shape[time_dimension] == durations_shape[0],
            "The size of the `time_dimension` of `values` must be equal to the length"
            " of `durations`.",
            {
                "time_dimension": time_dimension,
                "values": values,
                "durations": durations,
            },
        )
        for index, duration in enumerate(durations):
            check_duration(duration, f"durations[{index}]")
        if time_dimension < 0:
            time_dimension = len(value_shape) + time_dimension
        return PwcNodeData(
            _operation,
            value_shape=value_shape[time_dimension + 1 :],
            durations=durations,
            batch_shape=value_shape[:time_dimension],
        )


@deprecated_node("pwc")  # deprecated 2021/05/20
class TensorPwc(Pwc):
    """Deprecated node."""

    name = "tensor_pwc"


class PwcSignal(Node):
    r"""
    Creates a piecewise-constant signal (scalar-valued function of time).

    Use this function to create a piecewise-constant signal in which the
    constant segments all have the same duration.

    Parameters
    ----------
    values : np.ndarray or Tensor
        The values :math:`\{\alpha_n\}` of the :math:`N` constant segments.
        These can represent either a single sequence of segment values or a
        batch of them. To create a batch of
        :math:`B_1 \times \ldots \times B_n` signals, represent these
        `values` as a tensor of shape
        :math:`B_1 \times \ldots \times B_n \times N`.
    duration : float
        The total duration :math:`\tau` of the signal.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The piecewise-constant function of time :math:`\alpha(t)`, satisfying
        :math:`\alpha(t)=\alpha_n` for :math:`t_{n-1}\leq t\leq t_n`, where
        :math:`t_n=n\tau/N` (where :math:`N` is the number of values
        in :math:`\{\alpha_n\}`). If you provide a batch of values, the
        returned `Pwc` represents a corresponding batch of
        :math:`B_1 \times \ldots \times B_n` functions :math:`\alpha(t)`.

    See Also
    --------
    complex_pwc_signal : Create complex `Pwc` signals from their moduli and phases.
    pwc : Corresponding operation with support for segments of different durations.
    pwc_operator : Create `Pwc` operators.
    pwc_sum : Sum multiple `Pwc`\s.
    symmetrize_pwc : Symmetrize `Pwc`\s.
    """

    name = "pwc_signal"
    args = [
        forge.arg("values", type=Union[np.ndarray, types.Tensor]),
        forge.arg("duration", type=float),
    ]
    rtype = types.Pwc

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        values = kwargs.get("values")
        duration = kwargs.get("duration")
        check_argument_numeric(values, "values")
        check_duration(duration, "duration")
        shape = validate_shape(values, "values")
        check_argument(
            len(shape) > 0,
            "The shape of values must have at least one dimension.",
            {"values": values},
        )
        durations = duration / shape[-1] * np.ones(shape[-1])
        return PwcNodeData(
            _operation,
            value_shape=(),
            durations=durations,
            batch_shape=shape[:-1],
        )


class ComplexPwcSignal(Node):
    r"""
    Creates a complex piecewise-constant signal from moduli and phases.

    Use this function to create a complex piecewise-constant signal from
    moduli and phases defined for each segment, in which the constant segments
    all have the same duration.

    Parameters
    ----------
    moduli : np.ndarray(real) or Tensor(real)
        The moduli :math:`\{\Omega_n\}` of the values of :math:`N` constant
        segments. These can represent either the moduli of a single
        sequence of segment values or of a batch of them. To provide a
        batch of sequences of segment values of shape
        :math:`B_1 \times \ldots \times B_n`, represent these moduli as a
        tensor of shape :math:`B_1 \times \ldots \times B_n \times N`.
    phases : np.ndarray(real) or Tensor(real)
        The phases :math:`\{\phi_n\}` of the complex segment values. Must
        have the same length as `moduli` (or same shape, if you're
        providing a batch).
    duration : float
        The total duration :math:`\tau` of the signal.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc(complex)
        The piecewise-constant function of time :math:`v(t)`, satisfying
        :math:`v(t)=\Omega_n e^{i\phi_n}` for :math:`t_{n-1}\leq t\leq t_n`,
        where :math:`t_n=n\tau/N` (where :math:`N` is the number of
        values in :math:`\{\Omega_n\}` and :math:`\{\phi_n\}`). If you
        provide a batch of `moduli` and `phases`, the returned `Pwc`
        represents a corresponding batch of
        :math:`B_1 \times \ldots \times B_n` functions :math:`v(t)`.

    See Also
    --------
    pwc_signal : Create `Pwc` signals from (possibly complex) values.
    """

    name = "complex_pwc_signal"
    args = [
        forge.arg("moduli", type=Union[np.ndarray, types.Tensor]),
        forge.arg("phases", type=Union[np.ndarray, types.Tensor]),
        forge.arg("duration", type=float),
    ]
    rtype = types.Pwc

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        moduli = kwargs.get("moduli")
        phases = kwargs.get("phases")
        duration = kwargs.get("duration")
        check_argument_numeric(moduli, "moduli")
        check_argument_numeric(phases, "phases")
        check_duration(duration, "duration")
        moduli_shape = validate_shape(moduli, "moduli")
        phases_shape = validate_shape(phases, "phases")
        check_argument(
            len(moduli_shape) > 0,
            "The shape of moduli must have at least one dimension.",
            {"moduli": moduli},
        )
        check_argument(
            moduli_shape == phases_shape,
            "The shape of moduli and phases must be equal.",
            {"moduli": moduli, "phases": phases},
        )
        durations = duration / moduli_shape[-1] * np.ones(moduli_shape[-1])
        return PwcNodeData(
            _operation,
            value_shape=(),
            durations=durations,
            batch_shape=moduli_shape[:-1],
        )


class PwcOperator(Node):
    r"""
    Creates a constant operator multiplied by a piecewise-constant signal.

    Parameters
    ----------
    signal : Pwc
        The piecewise-constant signal :math:`a(t)`, or a batch of
        piecewise-constant signals.
    operator : np.ndarray or Tensor
        The operator :math:`A`. It must have two equal dimensions.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The piecewise-constant operator :math:`a(t)A` (or a batch of
        piecewise-constant operators, if you provide a batch of
        piecewise-constant signals).

    See Also
    --------
    complex_pwc_signal : Create complex `Pwc` signals from their moduli and phases.
    constant_pwc_operator : Create constant `Pwc`\s.
    pwc : Create piecewise-constant functions.
    pwc_operator_hermitian_part : Hermitian part of a piecewise-constant operator.
    pwc_signal : Create `Pwc` signals from (possibly complex) values.
    pwc_sum : Sum multiple `Pwc`\s.
    stf_operator : Corresponding operation for `Stf`\s.
    stf_operator_hermitian_part : Corresponding operation for `Stf`\s.
    """

    name = "pwc_operator"
    args = [
        forge.arg("signal", type=types.Pwc),
        forge.arg("operator", type=Union[np.ndarray, types.Tensor]),
    ]
    rtype = types.Pwc

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        signal = kwargs.get("signal")
        operator = kwargs.get("operator")
        check_argument(
            isinstance(signal, PwcNodeData),
            "The signal must be a Pwc.",
            {"signal": signal},
        )
        batch_shape, signal_value_shape = validate_batch_and_value_shapes(
            signal, "signal"
        )
        check_argument(
            signal_value_shape == (),
            "The signal must be scalar-valued.",
            {"signal": signal},
        )

        value_shape = validate_shape(operator, "operator")
        check_operator(operator, "operator")
        check_argument(
            len(value_shape) == 2,
            "The operator must be a matrix, not a batch.",
            {"operator": operator},
            extras={"operator.shape": value_shape},
        )
        return PwcNodeData(
            _operation,
            value_shape=value_shape,
            durations=signal.durations,
            batch_shape=batch_shape,
        )


class ConstantPwcOperator(Node):
    r"""
    Creates a constant piecewise-constant operator over a specified duration.

    Parameters
    ----------
    duration : float
        The duration :math:`\tau` for the resulting piecewise-constant
        operator.
    operator : np.ndarray or Tensor
        The operator :math:`A`, or a batch of operators. It must have at
        least two dimensions, and its last two dimensions must be equal.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The constant operator :math:`t\mapsto A` (for :math:`0\leq t\leq\tau`)
        (or a batch of constant operators, if you provide a batch of operators).

    See Also
    --------
    constant_stf_operator : Corresponding operation for `Stf`\s.
    pwc_operator : Create `Pwc` operators.
    pwc_operator_hermitian_part : Hermitian part of a piecewise-constant operator.
    """

    name = "constant_pwc_operator"
    args = [
        forge.arg("duration", type=float),
        forge.arg("operator", type=Union[np.ndarray, types.Tensor]),
    ]
    rtype = types.Pwc

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        duration = kwargs.get("duration")
        operator = kwargs.get("operator")
        check_duration(duration, "duration")
        shape = validate_shape(operator, "operator")
        check_operator(operator, "operator")
        return PwcNodeData(
            _operation,
            value_shape=shape[-2:],
            durations=np.array([duration]),
            batch_shape=shape[:-2],
        )


class ConstantPwc(Node):
    r"""
    Creates a piecewise-constant (PWC) function of time that is constant over a specified duration.

    Parameters
    ----------
    constant : number or np.ndarray or Tensor
        The value :math:`c` of the function on the constant segment.
        To create a batch of :math:`B_1 \times \ldots \times B_n` piecewise-constant
        functions of shape :math:`D_1 \times \ldots \times D_m`, provide this `constant`
        parameter as an object of shape
        :math:`B_1\times\ldots\times B_n\times D_1\times\ldots\times D_m`.
    duration : float
        The duration :math:`\tau` for the resulting piecewise-constant function.
    batch_dimension_count : int, optional
        The number of batch dimensions, :math:`n` in `constant`.
        If provided, the first :math:`n` dimensions of `constant` are considered batch dimensions.
        Defaults to 0, which corresponds to no batch.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The constant function :math:`f(t) = c` (for :math:`0\leq t\leq\tau`)
        (or a batch of constant functions, if you provide `batch_dimension_count`).

    See Also
    --------
    constant_pwc_operator : Create constant `Pwc` operators.
    constant_stf : Corresponding operation for `Stf`\s.
    pwc : Create piecewise-constant functions.
    """

    name = "constant_pwc"
    args = [
        forge.arg("constant", type=Union[float, complex, np.ndarray, types.Tensor]),
        forge.arg("duration", type=float),
        forge.arg("batch_dimension_count", type=int, default=0),
    ]
    rtype = types.Pwc

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        constant = kwargs.get("constant")
        duration = kwargs.get("duration")
        batch_dimension_count = kwargs.get("batch_dimension_count")

        check_argument_numeric(constant, "constant")
        check_duration(duration, "duration")
        check_argument_integer(batch_dimension_count, "batch_dimension_count")

        shape = validate_shape(constant, "constant")
        check_argument(
            len(shape) >= batch_dimension_count,
            "The number of batch dimensions must not be larger than the number "
            "of dimensions of the input constant.",
            {"constant": constant, "batch_dimension_count": batch_dimension_count},
            {"Number of value dimensions": len(shape)},
        )
        check_argument(
            batch_dimension_count >= 0,
            "The number of batch dimensions must not be negative.",
            {"batch_dimension_count": batch_dimension_count},
        )

        return PwcNodeData(
            _operation,
            value_shape=shape[batch_dimension_count:],
            durations=np.array([duration]),
            batch_shape=shape[:batch_dimension_count],
        )


class PwcOperatorHermitianPart(Node):
    r"""
    Creates the Hermitian part of a piecewise-constant operator.

    Parameters
    ----------
    operator : Pwc
        The operator :math:`A(t)`, or a batch of operators.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The Hermitian part :math:`\frac{1}{2}(A(t)+A^\dagger(t))`
        (or a batch of Hermitian parts, if you provide a batch of operators).

    See Also
    --------
    constant_pwc_operator : Create constant `Pwc`\s.
    pwc_operator : Create `Pwc` operators.
    """

    name = "pwc_operator_hermitian_part"
    args = [
        forge.arg("operator", type=types.Pwc),
    ]
    rtype = types.Pwc

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        operator = kwargs.get("operator")
        check_argument(
            isinstance(operator, PwcNodeData),
            "The operator must be a Pwc.",
            {"operator": operator},
        )
        batch_shape, value_shape = validate_batch_and_value_shapes(
            operator,
            "operator",
        )
        return PwcNodeData(
            _operation,
            value_shape=value_shape,
            durations=operator.durations,
            batch_shape=batch_shape,
        )


class PwcSum(Node):
    r"""
    Creates the sum of multiple piecewise-constant terms.

    Parameters
    ----------
    terms : list[Pwc]
        The individual piecewise-constant terms :math:`\{v_j(t)\}` to sum. All
        terms must have the same duration, values of the same shape, and the
        same batch shape, but may have different segmentations (different
        numbers of segments of different durations) and different dtypes of
        segment values.

    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The piecewise-constant function (or batch of functions) of time
        :math:`\sum_j v_j(t)`. Its values have the same shape as the values of
        each of the `terms` that you provided. If each of the `terms` represents
        a batch of functions, this result represents a batch of functions with
        the same batch shape. If any `term` has complex-valued segments, the
        value of the returned Pwc is complex, otherwise is float.

    See Also
    --------
    discretize_stf : Discretize an `Stf` into a `Pwc`.
    pwc : Create piecewise-constant functions.
    pwc_operator : Create `Pwc` operators.
    pwc_signal : Create `Pwc` signals from (possibly complex) values.
    stf_sum : Corresponding operation for `Stf`\s.
    """

    name = "pwc_sum"
    args = [forge.arg("terms", type=List[types.Pwc])]
    rtype = types.Pwc

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        terms = kwargs.get("terms")
        check_argument_iteratable(terms, "terms")
        check_argument(
            all(isinstance(term, PwcNodeData) for term in terms),
            "Each of the terms must be a Pwc.",
            {"terms": terms},
        )
        batch_shape, value_shape = validate_batch_and_value_shapes(
            terms[0],
            "terms[0]",
        )
        check_argument(
            all(
                (
                    (term.value_shape == value_shape)
                    and (term.batch_shape == batch_shape)
                )
                for term in terms[1:]
            ),
            "All the terms must have the same shape.",
            {"terms": terms},
        )
        check_argument(
            all(
                np.allclose(np.sum(terms[0].durations), np.sum(term.durations))
                for term in terms
            ),
            "All the terms must have the same total duration.",
            {"terms": terms},
            extras={
                "total duration of each term": [
                    np.sum(term.durations) for term in terms
                ]
            },
        )
        upsampled_durations = np.diff(
            np.insert(
                np.unique(
                    np.concatenate([np.cumsum(term.durations) for term in terms])
                ),
                0,
                0,
            )
        )
        return PwcNodeData(
            _operation,
            value_shape=value_shape,
            durations=upsampled_durations,
            batch_shape=batch_shape,
        )


class RealFourierPwcSignal(Node):
    r"""
    Creates a piecewise-constant signal constructed from Fourier components.

    Use this function to create a signal defined in terms of Fourier
    (sine/cosine) basis signals that can be optimized by varying their
    coefficients and, optionally, their frequencies.

    Parameters
    ----------
    duration : float
        The total duration :math:`\tau` of the signal.
    segment_count : int
        The number of segments :math:`N` to use for the piecewise-constant
        approximation.
    initial_coefficient_lower_bound : float, optional
        The lower bound :math:`c_\mathrm{min}` on the initial coefficient
        values. Defaults to -1.
    initial_coefficient_upper_bound : float, optional
        The upper bound :math:`c_\mathrm{max}` on the initial coefficient
        values. Defaults to 1.
    fixed_frequencies : list[float], optional
        The fixed non-zero frequencies :math:`\{f_m\}` to use for the Fourier
        basis. Must be non-empty if provided. Must be specified in the inverse
        units of `duration` (for example if `duration` is in seconds, these
        values must be given in Hertz).
    optimizable_frequency_count : int, optional
        The number of non-zero frequencies :math:`M` to use, if the
        frequencies can be optimized. Must be greater than zero if provided.
    randomized_frequency_count : int, optional
        The number of non-zero frequencies :math:`M` to use, if the
        frequencies are to be randomized but fixed. Must be greater than zero
        if provided.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc(1D, real)
        The optimizable, real-valued, piecewise-constant signal built from the
        appropriate Fourier components.

    Warnings
    --------
    You must provide exactly one of `fixed_frequencies`, `optimizable_variable`,
    or `randomized_frequency_count`.

    See Also
    --------
    real_fourier_stf_signal : Corresponding operation for `Stf`.

    Notes
    -----
    This function sets the basis signal frequencies :math:`\{f_m\}`
    depending on the chosen mode:

    * For fixed frequencies, you provide the frequencies directly.
    * For optimizable frequencies, you provide the number of frequencies
      :math:`M`, and this function creates :math:`M` unbounded optimizable
      variables :math:`\{f_m\}`, with initial values in the ranges
      :math:`\{[(m-1)/\tau, m/\tau]\}`.
    * For randomized frequencies, you provide the number of frequencies
      :math:`M`, and this function creates :math:`M` randomized constants
      :math:`\{f_m\}` in the ranges :math:`\{[(m-1)/\tau, m/\tau]\}`.

    After this function creates the :math:`M` frequencies :math:`\{f_m\}`, it
    produces the signal

    .. math::
        \alpha^\prime(t) = v_0 +
        \sum_{m=1}^M [ v_m \cos(2\pi t f_m) + w_m \sin(2\pi t f_m) ],

    where :math:`\{v_m,w_m\}` are (unbounded) optimizable variables, with
    initial values bounded by :math:`c_\mathrm{min}` and
    :math:`c_\mathrm{max}`. This function produces the final
    piecewise-constant signal :math:`\alpha(t)` by sampling
    :math:`\alpha^\prime(t)` at :math:`N` equally spaced points along the
    duration :math:`\tau`, and using those sampled values as the constant
    segment values.

    You can use the signals created by this function for chopped random basis
    (CRAB) optimization [1]_.

    References
    ----------
    .. [1] `P. Doria, T. Calarco, and S. Montangero, Physical Review Letters 106, 190501 (2011).
           <https://doi.org/10.1103/PhysRevLett.106.190501>`_
    """

    name = "real_fourier_pwc_signal"
    optimizable_variable = True
    args = [
        forge.arg("duration", type=float),
        forge.arg("segment_count", type=int),
        forge.arg("initial_coefficient_lower_bound", type=float, default=-1),
        forge.arg("initial_coefficient_upper_bound", type=float, default=1),
        forge.arg("fixed_frequencies", type=Optional[List[float]], default=None),
        forge.arg("optimizable_frequency_count", type=Optional[int], default=None),
        forge.arg("randomized_frequency_count", type=Optional[int], default=None),
    ]
    rtype = types.Pwc

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        duration = kwargs.get("duration")
        segment_count = kwargs.get("segment_count")
        check_duration(duration, "duration")

        check_argument_integer(segment_count, "segment_count")
        check_argument(
            segment_count > 0,
            "The number of segments must be greater than zero.",
            {"segment_count": segment_count},
        )

        fixed_frequencies = kwargs.get("fixed_frequencies")
        optimizable_frequency_count = kwargs.get("optimizable_frequency_count")
        randomized_frequency_count = kwargs.get("randomized_frequency_count")
        validate_inputs_real_fourier_signal(
            fixed_frequencies, optimizable_frequency_count, randomized_frequency_count
        )

        durations = duration / segment_count * np.ones(segment_count)

        return PwcNodeData(
            _operation,
            value_shape=(),
            durations=durations,
            batch_shape=(),
        )


class SymmetrizePwc(Node):
    r"""
    Creates the symmetrization of a piecewise-constant function.

    Parameters
    ----------
    pwc : Pwc
        The piecewise-constant function :math:`v(t)` to symmetrize.
    name : str, optional
        The name of the node.

    Returns
    -------
    Pwc
        The piecewise-constant function :math:`w(t)` defined by
        :math:`w(t)=v(t)` for :math:`0\leq t\leq \tau` and
        :math:`w(t)=v(2\tau-t)` for :math:`\tau\leq t\leq 2\tau`, where
        :math:`\tau` is the duration of :math:`v(t)`.

    See Also
    --------
    pwc_signal : Create `Pwc` signals from (possibly complex) values.
    """

    name = "symmetrize_pwc"
    args = [forge.arg("pwc", type=types.Pwc)]
    rtype = types.Pwc

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        pwc = kwargs.get("pwc")
        check_argument(
            isinstance(pwc, PwcNodeData),
            "The pwc parameter must be a Pwc.",
            {"pwc": pwc},
        )
        batch_shape, value_shape = validate_batch_and_value_shapes(
            pwc,
            "pwc",
        )
        symmetrized_durations = np.concatenate((pwc.durations, pwc.durations[::-1]))
        return PwcNodeData(
            _operation,
            value_shape=value_shape,
            durations=symmetrized_durations,
            batch_shape=batch_shape,
        )


class TimeEvolutionOperatorsPwc(Node):
    """
    Calculates the unitary time-evolution operators for a system defined by a piecewise-constant
    Hamiltonian.

    Parameters
    ----------
    hamiltonian : Pwc
        The control Hamiltonian, or batch of control Hamiltonians.
    sample_times : np.ndarray(1D, real)
        The N times at which you want to sample the unitaries. Must be ordered and contain
        at least one element.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        Tensor of shape [..., N, D, D], representing the unitary time evolution.
        The n-th element (along the -3 dimension) represents the unitary (or batch of unitaries)
        from t = 0 to ``sample_times[n]``.

    See Also
    --------
    state_evolution_pwc : Evolve a quantum state.
    time_evolution_operators_stf : Corresponding operation for `Stf` Hamiltonians.
    """

    name = "time_evolution_operators_pwc"
    args = [
        forge.arg("hamiltonian", type=types.Pwc),
        forge.arg("sample_times", type=np.ndarray),
    ]
    rtype = types.Tensor

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        hamiltonian = kwargs.get("hamiltonian")
        sample_times = kwargs.get("sample_times")
        check_argument(
            isinstance(hamiltonian, PwcNodeData),
            "The Hamiltonian must be a Pwc.",
            {"hamiltonian": hamiltonian},
        )
        batch_shape, value_shape = validate_batch_and_value_shapes(
            hamiltonian,
            "hamiltonian",
        )
        check_sample_times(sample_times, "sample_times")
        validate_hamiltonian(hamiltonian, "hamiltonian")
        time_count = len(sample_times)
        shape = batch_shape + (time_count,) + value_shape
        return TensorNodeData(_operation, shape=shape)


class SamplePwc(Node):
    r"""
    Samples a Pwc at the given times.

    Parameters
    ----------
    pwc : Pwc
        The Pwc to sample.
    sample_times : np.ndarray(1D, real)
        The times at which you want to sample the Pwc. Must be ordered, contain
        at least one element, and lie between 0 and the duration of the Pwc.
        For a sample time :math:`t` the returned value
        lies in the half open interval :math:`t_{j-1} < t \leq t_j`, where
        :math:`t_j` indicates the boundary of a segment.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The values of the Pwc at the given times.

    See Also
    --------
    sample_stf : Sample an `Stf` at given times.
    """

    name = "sample_pwc"
    args = [
        forge.arg("pwc", type=types.Pwc),
        forge.arg("sample_times", type=np.ndarray),
    ]
    rtype = types.Tensor

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        pwc = kwargs.get("pwc")
        check_argument(
            isinstance(pwc, PwcNodeData), "The pwc must be a Pwc.", {"pwc": pwc}
        )
        batch_shape, value_shape = validate_batch_and_value_shapes(pwc, "pwc")
        sample_times = kwargs.get("sample_times")
        check_sample_times(sample_times, "sample_times")
        check_argument(
            sample_times[0] >= 0,
            "The first sample time can't be smaller than zero.",
            {"sample_times": sample_times},
        )
        check_argument(
            sample_times[-1] <= np.sum(pwc.durations),
            "The last sample time can't be larger than the duration of the Pwc.",
            {"sample_times": sample_times},
            extras={"Pwc durations": pwc.durations},
        )
        time_count = len(sample_times)
        shape = batch_shape + (time_count,) + value_shape
        return TensorNodeData(_operation, shape=shape)
