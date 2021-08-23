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
"""Module for generic nodes defined in core."""
from typing import (
    List,
    Optional,
    Union,
)

import forge
import numpy as np

from qctrlcommons.node import types
from qctrlcommons.node.base import Node
from qctrlcommons.node.node_data import (
    TargetNodeData,
    TensorNodeData,
)
from qctrlcommons.node.utils import validate_shape
from qctrlcommons.preconditions import (
    check_argument,
    check_argument_iteratable,
    check_argument_nonzero,
    check_argument_numeric,
    check_argument_orthogonal_projection_operator,
    check_argument_partial_isometry,
    check_operator,
)


class Target(Node):
    r"""
    Creates information about the target for system time evolution.

    Nodes created with this function contain two types of information: the
    target gate for the system time evolution, and the projection operator
    that defines the subspace of interest for robustness.

    Parameters
    ----------
    operator : np.ndarray or Tensor
         The target gate :math:`U_\mathrm{target}`. Must be a non-zero partial
         isometry.
    filter_function_projector : np.ndarray, optional
        The orthogonal projection matrix :math:`P` onto the subspace used for
        filter function calculations. If you provide a value then it must be
        Hermitian and idempotent. Defaults to the identity matrix.

    Returns
    -------
    Target
        The node containing the specified target information.

    See Also
    --------
    infidelity_pwc : Total infidelity of a system with a piecewise-constant Hamiltonian.
    infidelity_stf : Total infidelity of a system with a sampleable Hamiltonian.

    Notes
    -----
    The target gate :math:`U_\mathrm{target}` is a non-zero partial isometry,
    which means that it can be expressed in the form
    :math:`\sum_j \left|\psi_j\right>\left<\phi_j\right|`, where
    :math:`\left\{\left|\psi_j\right>\right\}` and
    :math:`\left\{\left|\phi_j\right>\right\}` both form (non-empty)
    orthonormal, but not necessarily complete, sets. Such a target represents
    a target state :math:`\left|\psi_j\right>` for each initial state
    :math:`\left|\phi_j\right>`. The resulting operational infidelity is 0
    if and only if, up to global phase, each initial state
    :math:`\left|\phi_j\right>` maps exactly to the corresponding final state
    :math:`\left|\psi_j\right>`.

    The filter function projector :math:`P` is an orthogonal projection
    matrix, which means that it satisfies :math:`P=P^\dagger=P^2`. The image
    of :math:`P` defines the set of initial states from which the calculated
    filter function measures robustness.
    """

    name = "target"
    args = [
        forge.arg("operator", type=Union[np.ndarray, types.Tensor]),
        forge.arg("filter_function_projector", type=Optional[np.ndarray], default=None),
    ]
    kwargs = {}  # Target should not accept `name` as parameter
    rtype = types.Target

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        operator = kwargs.get("operator")
        value_shape = validate_shape(operator, "operator")

        if isinstance(operator, np.ndarray):
            check_argument_numeric(operator, "operator")
            check_argument_partial_isometry(operator, "operator")
            check_argument_nonzero(operator, "operator")
        else:
            check_operator(operator, "operator")
            check_argument(
                len(value_shape) == 2,
                "The operator must be a matrix, not a batch.",
                {"operator": operator},
                extras={"operator.shape": value_shape},
            )

        filter_function_projector = kwargs.get("filter_function_projector")
        if filter_function_projector is not None:
            check_argument_numeric(
                filter_function_projector, "filter_function_projector"
            )
            check_argument_orthogonal_projection_operator(
                filter_function_projector, "filter_function_projector"
            )

        return TargetNodeData(_operation, value_shape=value_shape)


class AnchoredDifferenceBoundedVariables(Node):
    r"""
    Creates a sequence of variables with an anchored difference bound.

    Use this function to create a sequence of optimization variables that have
    a difference bound (each variable is constrained to be within a given
    distance of the adjacent variables) and are anchored to zero at the start
    and end (the initial and final variables are within a given distance of
    zero).

    Parameters
    ----------
    count : int
        The number :math:`N` of individual real-valued variables to create.
    lower_bound : float
        The lower bound :math:`v_\mathrm{min}` on the variables.
        The same lower bound applies to all `count` individual variables.
    upper_bound : float
        The upper bound :math:`v_\mathrm{max}` on the variables.
        The same upper bound applies to all `count` individual variables.
    difference_bound : float
        The difference bound :math:`\delta` to enforce between adjacent
        variables.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The sequence :math:`\{v_n\}` of :math:`N` anchored difference-bounded
        optimization variables, satisfying
        :math:`v_\mathrm{min}\leq v_n\leq v_\mathrm{max}`,
        :math:`|v_{n-1}-v_n|\leq\delta` for :math:`2\leq n\leq N`,
        :math:`|v_1|\leq\delta`, and :math:`|v_N|\leq\delta`.

    See Also
    --------
    bounded_optimization_variable : Create bounded optimization variables.
    :func:`~qctrl.dynamic.namespaces.FunctionNamespace.calculate_optimization` : Find the minimum
        of generic functions.
    unbounded_optimization_variable : Create unbounded optimization variables.
    """

    name = "anchored_difference_bounded_variables"
    optimizable_variable = True
    args = [
        forge.arg("count", type=int),
        forge.arg("lower_bound", type=float),
        forge.arg("upper_bound", type=float),
        forge.arg("difference_bound", type=float),
    ]
    rtype = types.Tensor

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        count = kwargs.get("count")
        return TensorNodeData(_operation, shape=(count,))


class HessianMatrix(Node):
    r"""
    Calculates a single Hessian matrix for all the variables.

    The Hessian is a matrix containing all the second partial derivatives
    of the `tensor` with respect to the `variables`.

    Parameters
    ----------
    tensor : Tensor(scalar, real)
        The real scalar tensor :math:`T` whose Hessian matrix you want to
        calculate.
    variables : List[Tensor(real)]
        The list of real variables :math:`\{\theta_i\}` with respect to
        which you want to take the second partial derivatives of the
        tensor. If any of the tensors of the list is not scalar, this
        function treats each of the elements of the tensor as a different
        variable. It does this by flattening all tensors and concatenating
        them in the same sequence that you provided in this list.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor(2D, real)
        The real Hessian matrix :math:`H` containing the second partial
        derivatives of the `tensor` :math:`T` with respect to the
        `variables` :math:`\{\theta_i\}`.

    Warnings
    --------
    This function currently doesn't support calculating a Hessian matrix for
    a graph which includes a `infidelity_pwc` node if it involves a Hamiltonian
    with degenerate eigenvalues at any segment. In that case, the function
    returns a `nan` Hessian matrix.

    Notes
    -----
    The :math:`(i,j)` element of the Hessian contains the partial
    derivative of the `tensor` with respect to the ith and the jth
    `variables`:

    .. math::
        H_{i,j} = \frac{\partial^2 T}{\partial \theta_i \partial \theta_j}.

    The variables :math:`\{\theta_i\}` follow the same sequence as the
    input list of `variables`. If some of the `variables` are not scalars,
    this function flattens them and concatenates them in the same order of
    the list of `variables` that you provided to create the sequence of
    scalar variables :math:`\{\theta_i\}`.

    If you choose a negative log-likelihood as the tensor :math:`T`, you
    can use this Hessian as an estimate of the Fisher information matrix.
    """
    name = "hessian_matrix"
    args = [
        forge.arg("tensor", type=types.Tensor),
        forge.arg("variables", type=List[types.Tensor]),
    ]
    rtype = types.Tensor

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        tensor = kwargs.get("tensor")
        variables = kwargs.get("variables")
        check_argument(
            isinstance(tensor, TensorNodeData),
            "The tensor parameter must be a Tensor.",
            {"tensor": tensor},
        )
        tensor_shape = validate_shape(tensor, "tensor")
        check_argument(
            tensor_shape == (),
            "The tensor must be a scalar tensor.",
            {"tensor": tensor},
        )
        check_argument_iteratable(variables, "variables")
        check_argument(
            all(isinstance(variable, TensorNodeData) for variable in variables),
            "Each of the variables must be a Tensor.",
            {"variables": variables},
        )
        variable_count = sum(
            [
                np.prod(validate_shape(variable, f"variables[{n}]"), dtype=int)
                for n, variable in enumerate(variables)
            ]
        )
        shape = (variable_count, variable_count)
        return TensorNodeData(_operation, shape=shape)


class Concatenate(Node):
    """
    Concatenates a list of tensors along a specified dimension.

    Parameters
    ----------
    tensors : List[np.ndarray or Tensor]
        The list of tensors that you want to concatenate. All of them must have the
        same shape in all dimensions except `axis`.
    axis : int
        The dimension along which you want to concatenate the tensors.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        The concatenated tensor.
    """

    name = "concatenate"
    args = [
        forge.arg("tensors", type=List[Union[np.ndarray, types.Tensor]]),
        forge.arg("axis", type=int),
    ]
    rtype = types.Tensor

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        tensors = kwargs.get("tensors")
        axis = kwargs.get("axis")
        check_argument_iteratable(tensors, "tensors")
        tensor_shapes = []
        for index, tensor in enumerate(tensors):
            check_argument_numeric(tensor, f"tensors[{index}]")
            tensor_shape = validate_shape(tensor, f"tensors[{index}]")
            tensor_shapes.append(tensor_shape)
            check_argument(
                (tensor_shape[:axis] + tensor_shape[axis + 1 :])
                == (tensor_shapes[0][:axis] + tensor_shape[axis + 1 :]),
                "All tensors must have the same size in every dimension,"
                " except in the dimension of axis.",
                {"tensors": tensors},
                extras={
                    "tensors[0].shape": tensor_shapes[0],
                    f"tensors[{index}].shape": tensor_shape,
                },
            )
        shape = (
            tensor_shapes[0][:axis]
            + (sum([tensor_shape[axis] for tensor_shape in tensor_shapes]),)
            + tensor_shapes[0][axis + 1 :]
        )
        return TensorNodeData(_operation, shape=shape)
