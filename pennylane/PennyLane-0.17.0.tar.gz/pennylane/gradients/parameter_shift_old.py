# Copyright 2018-2021 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
This module contains functions for computing the parameter-shift gradient
of a qubit quantum tape.
"""
# pylint: disable=protected-access
import functools

import numpy as np
import pennylane as qml

from .finite_difference import grad as numeric_pd


def expval_grad(tape, idx, gradient_recipe=None, shift=np.pi / 2):
    r"""Generate the parameter-shift tapes and postprocessing methods required
    to compute the gradient of an gate parameter with respect to an
    expectation value.

    Args:
        tape (.QuantumTape): quantum tape to differentiate
        idx (int): trainable parameter index to differentiate with respect to
        gradient_recipe (list[list[float]] or None): Gradient recipe for the
            parameter-shift method.

            This is a nested list containing elements of the form
            :math:`[c_i, a_i, s_i]` where :math:`i` is the index of the
            term, resulting in a gradient recipe of

            .. math:: \frac{\partial}{\partial\phi_k}f = \sum_{i} c_i f(a_i \phi_k + s_i).

            If ``None``, the default gradient recipe containing the two terms
            :math:`[c_0, a_0, s_0]=[1/2, 1, \pi/2]` and :math:`[c_1, a_1,
            s_1]=[-1/2, 1, -\pi/2]` is assumed.
        shift (float): The shift value to use for the two-term parameter-shift formula.
            Only valid if the operation in question supports the two-term parameter-shift
            rule (that is, it has two distinct eigenvalues) and ``gradient_recipe``
            is ``None``.

    Returns:
        tuple[list[QuantumTape], function]: A tuple containing the list of generated tapes,
        in addition to a post-processing function to be applied to the evaluated
        tapes.

    **Gradients of expectation values**

    For a variational evolution :math:`U(\mathbf{p}) \vert 0\rangle` with
    :math:`N` parameters :math:`\mathbf{p}`,
    consider the expectation value of an observable :math:`O`:

    .. math::

        f(\mathbf{p})  = \langle \hat{O} \rangle(\mathbf{p}) = \langle 0 \vert
        U(\mathbf{p})^\dagger \hat{O} U(\mathbf{p}) \vert 0\rangle.


    The gradient of this expectation value can be calculated using :math:`2N` expectation
    values using the parameter-shift rule:

    .. math::

        \frac{\partial f}{\partial \mathbf{p}} = \frac{1}{2\sin s} \left[ f(\mathbf{p} + s) -
        f(\mathbf{p} -s) \right].

    """
    t_idx = list(tape.trainable_params)[idx]
    op = tape._par_info[t_idx]["op"]
    p_idx = tape._par_info[t_idx]["p_idx"]

    if gradient_recipe is None:
        gradient_recipe = op.get_parameter_shift(p_idx, shift=shift)

    params = qml.math.stack(tape.get_parameters())
    shift = np.zeros(qml.math.shape(params))
    coeffs = []
    tapes = []

    for c, a, s in gradient_recipe:
        shift[idx] = s
        shifted_tape = tape.copy(copy_operations=True)
        shifted_params = a * params + qml.math.convert_like(shift, params)
        shifted_tape.set_parameters(qml.math.unstack(shifted_params))

        coeffs.append(c)
        tapes.append(shifted_tape)

    def processing_fn(results):
        """Computes the gradient of the parameter at index idx via the
        parameter-shift method.

        Args:
            results (list[real]): evaluated quantum tapes

        Returns:
            array[float]: 1-dimensional array of length determined by the tape output
            measurement statistics
        """
        results = qml.math.squeeze(qml.math.stack(results))
        return sum([c * r for c, r in zip(coeffs, results)])

    return tapes, processing_fn


def _generate_variance_tapes(tape, var_idx):
    """Given an input tape with terminal variance measurements,
    return a copy of the tape with only terminal expectation values.
    In addition, if there are non-involutary observables measured,
    a second tape is returned with the observable replaced with its square.
    """
    # Get <A>, the expectation value of the tape with unshifted parameters.
    expval_tape = tape.copy(copy_operations=True)
    expval_sq_tape = None

    # Convert all variance measurements on the tape into expectation values
    for i in var_idx:
        obs = expval_tape._measurements[i].obs
        expval_tape._measurements[i] = qml.measure.MeasurementProcess(
            qml.operation.Expectation, obs=obs
        )

    # For involutory observables (A^2 = I) we have d<A^2>/dp = 0.
    # Currently, the only observable we have in PL that may be non-involutory is qml.Hermitian
    involutory = [i for i in var_idx if tape.observables[i].name != "Hermitian"]

    # If there are non-involutory observables A present, we must compute d<A^2>/dp.
    non_involutory = set(var_idx) - set(involutory)

    if non_involutory:
        expval_sq_tape = tape.copy(copy_operations=True)

        for i in non_involutory:
            # We need to calculate d<A^2>/dp; to do so, we replace the
            # involutory observables A in the queue with A^2.
            obs = expval_sq_tape._measurements[i].obs
            A = obs.matrix

            obs = qml.Hermitian(A @ A, wires=obs.wires)
            expval_sq_tape._measurements[i] = qml.measure.MeasurementProcess(
                qml.operation.Expectation, obs=obs
            )

    return expval_tape, expval_sq_tape


def var_grad(
    tape,
    idx,
    gradient_recipe=None,
    shift=np.pi / 2,
    expval_tape=None,
    expval_sq_tape=None,
    f0=True,
):
    r"""Generate the parameter-shift tapes and postprocessing methods required
    to compute the gradient of a gate parameter with respect to a
    variance value.

    Args:
        tape (.QuantumTape): quantum tape to differentiate
        idx (int): trainable parameter index to differentiate with respect to
        gradient_recipe (list[list[float]] or None): Gradient recipe for the
            parameter-shift method.

            This is a nested list containing elements of the form
            :math:`[c_i, a_i, s_i]` where :math:`i` is the index of the
            term, resulting in a gradient recipe of

            .. math:: \frac{\partial}{\partial\phi_k}f = \sum_{i} c_i f(a_i \phi_k + s_i).

            If ``None``, the default gradient recipe containing the two terms
            :math:`[c_0, a_0, s_0]=[1/2, 1, \pi/2]` and :math:`[c_1, a_1,
            s_1]=[-1/2, 1, -\pi/2]` is assumed.
        shift (float): The shift value to use for the two-term parameter-shift formula.
            Only valid if the operation in question supports the two-term parameter-shift
            rule (that is, it has two distinct eigenvalues) and ``gradient_recipe``
            is ``None``.
        expval_tape (.QuantumTape or None): A copy of ``tape``, with all terminal
            variance measurements replaced with expectation values. If not provided,
            it will be computed automatically.
        expval_sq_tape (.QuantumTape or None): A copy of ``tape``, with all terminal
            variance measurements of non-involutary observables replaced with expectation
            values of the respective observable squared. If not provided, it will be
            computed automatically.
        f0 (bool): If ``True``, include a gradient tape for computing the result of
            ``expval_tape``. If ``False``, this will not be included in the output tapes
            to be executed.

    Returns:
        tuple[list[QuantumTape], function]: A tuple containing the list of generated tapes,
        in addition to a post-processing function to be applied to the evaluated
        tapes.

    **Gradients of variances**

    For a variational evolution :math:`U(\mathbf{p}) \vert 0\rangle` with
    :math:`N` parameters :math:`\mathbf{p}`,
    consider the variance of an observable :math:`O`:

    .. math::

        g(\mathbf{p})=\langle \hat{O}^2 \rangle (\mathbf{p}) - [\langle \hat{O}
        \rangle(\mathbf{p})]^2.

    We can relate this directly to the parameter-shift rule for
    :func:`expectation values <.parameter_shift.expval_grad>`
    :math:`f(\mathbf{p})  = \langle \hat{O} \rangle(\mathbf{p})` by noting that

    .. math::

        \frac{\partial g}{\partial \mathbf{p}}= \frac{\partial}{\partial
        \mathbf{p}} \langle \hat{O}^2 \rangle (\mathbf{p})
        - 2 f(\mathbf{p}) \frac{\partial f}{\partial \mathbf{p}}.

    This results in :math:`4N + 1` evaluations.

    In the case where :math:`O` is involutory (:math:`\hat{O}^2 = I`), the first term in the above
    expression vanishes, and we are simply left with

    .. math::

      \frac{\partial g}{\partial \mathbf{p}} = - 2 f(\mathbf{p})
      \frac{\partial f}{\partial \mathbf{p}},

    allowing us to compute the gradient using :math:`2N + 1` evaluations.
    """
    tapes = []
    var_mask = [m.return_type is qml.operation.Variance for m in tape.measurements]
    var_idx = np.where(var_mask)[0]

    if expval_tape is None:
        # Get <A>, the expectation value of the tape with unshifted parameters.
        expval_tape, expval_sq_tape = _generate_variance_tapes(tape, var_idx)

    # evaluate the analytic derivative of <A>
    pdA_tapes, pdA_fn = expval_grad(expval_tape, idx, gradient_recipe=gradient_recipe, shift=shift)
    tapes.extend(pdA_tapes)

    if expval_sq_tape is not None:
        # Non-involutory observables are present; the partial derivative of <A^2>
        # may be non-zero. Here, we calculate the analytic derivatives of the <A^2>
        # observables.
        involutory = [i for i in var_idx if tape.observables[i].name != "Hermitian"]
        pdA2_tapes, pdA2_fn = expval_grad(
            expval_sq_tape, idx, gradient_recipe=gradient_recipe, shift=shift
        )
        tapes.extend(pdA2_tapes)

    if f0:
        tapes.append(expval_tape)

    def processing_fn(results):
        """Computes the gradient of the parameter at index ``idx`` via the
        parameter-shift method for a circuit containing a mixture
        of expectation values and variances.

        Args:
            results (list[real]): evaluated quantum tapes

        Returns:
            array[float]: 1-dimensional array of length determined by the tape output
            measurement statistics
        """
        pdA = pdA_fn(results[0:2])
        pdA2 = 0

        if expval_sq_tape is not None:
            pdA2 = pdA2_fn(results[2:4])

            if involutory:
                qml.math.where(involutory, 0, pdA2)

        # Check if the expectation value of the tape with unshifted parameters
        # has already been calculated.
        if tape._var_f0 is None:
            # The expectation value hasn't been previously calculated;
            # it will be the last element of the `results` argument.
            tape._var_f0 = results[-1]

        # return d(var(A))/dp = d<A^2>/dp -2 * <A> * d<A>/dp for the variances,
        # d<A>/dp for plain expectations
        return qml.math.where(var_mask, pdA2 - 2 * tape._var_f0 * pdA, pdA)

    return tapes, processing_fn


def _gradient_analysis(tape):
    """Update the parameter information dictionary with gradient information
    of each parameter"""
    tape._gradient_fn = grad

    for idx, info in tape._par_info.items():

        if idx not in tape.trainable_params:
            info["grad_method"] = None
        else:
            op = tape._par_info[idx]["op"]

            if op.grad_method == "F":
                info["grad_method"] = "F"
            else:
                info["grad_method"] = tape._grad_method(idx, use_graph=True, default_method="A")


def grad(tape, argnum=None, shift=np.pi / 2, gradient_recipes=None, fallback_fn=numeric_pd):
    r"""Generate the parameter-shift tapes and postprocessing methods required
    to compute the gradient of an gate parameter with respect to an
    expectation value.

    Args:
        tape (.QuantumTape): quantum tape to differentiate
        argnum (int or list[int] or None): Trainable parameter indices to differentiate
            with respect to. If not provided, the derivative with respect to all
            trainable indices are returned.
        shift (float): The shift value to use for the two-term parameter-shift formula.
            Only valid if the operation in question supports the two-term parameter-shift
            rule (that is, it has two distinct eigenvalues) and ``gradient_recipe``
            is ``None``.
        gradient_recipes (tuple(list[list[float]] or None)): List of gradient recipes
            for the parameter-shift method. One gradient recipe must be provided
            per trainable parameter.

            This is a tuple with one nested list per parameter. For
            parameter :math:`\phi_k`, the nested list contains elements of the form
            :math:`[c_i, a_i, s_i]` where :math:`i` is the index of the
            term, resulting in a gradient recipe of

            .. math:: \frac{\partial}{\partial\phi_k}f = \sum_{i} c_i f(a_i \phi_k + s_i).

            If ``None``, the default gradient recipe containing the two terms
            :math:`[c_0, a_0, s_0]=[1/2, 1, \pi/2]` and :math:`[c_1, a_1,
            s_1]=[-1/2, 1, -\pi/2]` is assumed for every parameter.
        fallback_fn (None or Callable): a fallback grdient function to use for
            any parameters that do not support the parameter-shift rule.

    Returns:
        tuple[list[list[QuantumTape]], list[function]]: A tuple containing the nested
        list of generated tapes (one per trainable parameters),
        in addition to a list of post-processing function to be applied to the evaluated
        tapes.

    For a variational evolution :math:`U(\mathbf{p}) \vert 0\rangle` with
    :math:`N` parameters :math:`\mathbf{p}`,
    consider the expectation value of an observable :math:`O`:

    .. math::

        f(\mathbf{p})  = \langle \hat{O} \rangle(\mathbf{p}) = \langle 0 \vert
        U(\mathbf{p})^\dagger \hat{O} U(\mathbf{p}) \vert 0\rangle.


    The gradient of this expectation value can be calculated using :math:`2N` expectation
    values using the parameter-shift rule:

    .. math::

        \frac{\partial f}{\partial \mathbf{p}} = \frac{1}{2\sin s} \left[ f(\mathbf{p} + s) -
        f(\mathbf{p} -s) \right].

    For more details, including gradients of variances, see :func:`.parameter_shift.expval_grad`
    and :func:`.parameter_shift.var_grad`.

    **Example**

    >>> params = np.array([0.1, 0.2, 0.3], requires_grad=True)
    >>> with qml.tapes.QuantumTape() as tape:
    ...     qml.RX(params[0], wires=0)
    ...     qml.RY(params[1], wires=0)
    ...     qml.RZ(params[2], wires=0)
    ...     qml.expval(qml.PauliZ(0))
    ...     qml.var(qml.PauliZ(0))
    >>> gradient_tapes, fns = qml.gradients.parameter_shift.grad(tape)
    >>> len(gradient_tapes)
    """
    if any(m.return_type is qml.operation.State for m in tape.measurements):
        raise ValueError("Does not support circuits that return the state")

    # perform gradient method validation
    if getattr(tape, "_gradient_fn", None) != grad:
        _gradient_analysis(tape)

    # TODO: replace the JacobianTape._grad_method_validation
    # functionality before deprecation.
    method = "analytic" if fallback_fn is None else "best"
    diff_methods = tape._grad_method_validation(method)

    if not tape.trainable_params or all(g == "0" for g in diff_methods):
        # Either all parameters have grad method 0,
        # or there are no trainable parameters.
        return [[]], []

    gradient_tapes = {}
    processing_fns = {}
    par_shift_method = expval_grad

    # TODO: replace the JacobianTape._choose_params_with_methods
    # functionality before deprecation.
    method_map = list(tape._choose_params_with_methods(diff_methods, argnum))
    unsupported_params = {idx for idx, g in method_map if g == "F"}

    if unsupported_params:
        gs, fns = fallback_fn(tape, argnum=unsupported_params)

        for t_idx, g, f in zip(unsupported_params, gs, fns):
            gradient_tapes[t_idx] = g
            processing_fns[t_idx] = f

    # check if the quantum tape contains any variance measurements
    var_mask = [m.return_type is qml.operation.Variance for m in tape.measurements]
    var_required = any(var_mask)

    if var_required:
        # The tape contains variances.
        tape._var_f0 = None

        # Store the locations of any variance measurements
        # in the measurement queue.
        var_idx = np.where(var_mask)[0]

        # Set the correct parameter-shift function
        expval_tape, expval_sq_tape = _generate_variance_tapes(tape, var_idx)
        par_shift_method = functools.partial(
            var_grad, expval_tape=expval_tape, expval_sq_tape=expval_sq_tape
        )

    for idx, (t_idx, dm) in enumerate(method_map):
        if dm == "0" or dm[0] == "F":
            continue

        op = tape._par_info[t_idx]["op"]
        gr = gradient_recipes[idx] if gradient_recipes is not None else None

        if idx > 0 and var_required:
            # no need to recompute the f0 point, it would have been
            # computed in an earlier loop
            g_tapes, fn = par_shift_method(tape, t_idx, gradient_recipe=gr, shift=shift, f0=False)
        else:
            g_tapes, fn = par_shift_method(tape, t_idx, gradient_recipe=gr, shift=shift)

        gradient_tapes[t_idx] = g_tapes
        processing_fns[t_idx] = fn

    if unsupported_params:
        gradient_tapes = [value for key, value in sorted(gradient_tapes.items())]
        processing_fns = [value for key, value in sorted(processing_fns.items())]
        return gradient_tapes, processing_fns

    return gradient_tapes.values(), processing_fns.values()
