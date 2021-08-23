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
"""
Module for nodes related to open quantum systems.
"""


from typing import (
    List,
    Optional,
    Tuple,
    Union,
)

import forge
import numpy as np
from scipy.sparse import coo_matrix

from qctrlcommons.node import types
from qctrlcommons.node.base import Node
from qctrlcommons.node.node_data import (
    PwcNodeData,
    SparsePwcNodeData,
    TensorNodeData,
)
from qctrlcommons.node.utils import (
    check_argument,
    check_density_matrix_shape,
    check_lindblad_terms,
    check_oqs_hamiltonian,
)
from qctrlcommons.preconditions import (
    check_duration,
    check_operator,
    check_sample_times,
)


class EstimatedKrylovSubspaceDimensionArnoldi(Node):
    r"""
    Calculates an appropriate Krylov subspace dimension (:math:`k`) to use in the Arnoldi
    integrator while keeping the total error in the evolution below a given error tolerance.

    Parameters
    ----------
    hamiltonian_sample : Union[Tensor, np.ndarray, scipy.sparse.spmatrix]
        A Hamiltonian, a sample with couplings similar to those passed to the Arnoldi integrator.
    lindblad_terms : List[Tuple[float, Union[np.ndarray, sp.sparse.spmatrix]]]
        A list of pairs of constant positive decay rates and Lindblad operators with Hilbert space
        dimension D. If mixed types of operators are used, all operators get transformed into
        dense operators.
    duration : float
        The total evolution time.
    maximum_segment_duration : float
        The maximum duration of the piecewise-constant Hamiltonian segments.
    error_tolerance : float, optional
        Tolerance for the error in the whole integration (defined as the Frobenius norm of the
        difference with the exact solution).
        Defaults to 1e-6.
    seed : int, optional
        This function uses a random number generator which may be seeded with this int.
        If None, this function's result may vary between calls.
    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor
        Recommended value of :math:`k` to use in an Arnoldi integration with a Liouvillian from a
        Hamiltonian and Lindblad terms similar to the ones passed.

    See Also
    --------
    density_matrix_evolution_pwc : Evolve a quantum state in an open system.

    Notes
    -----
    To provide the recommended :math:`k` parameter, this function uses the bound in the error for
    the Arnoldi algorithm [1]_ [2]_ as an estimate for the error. For a single time step this gives

    .. math::
        \mathrm{error} \leq 12 e^{-\rho\tau} \left (\frac{e \rho \tau}{k}  \right )^{k}

    where :math:`\tau` is the time step and :math:`\rho` is a positive number such that the
    numerical range of the generator is contained in a disc of radius :math:`\rho` centered at
    :math:`(-\rho,0)` of the complex plane.

    As this bound overestimates the error, the actual resulting errors with the recommended
    parameter are expected to be (a few orders of magnitude) smaller than the requested tolerance.

    References
    ----------
    .. [1] `N. Del Buono and L. Lopez,
           Lecture Notes in Computer Science 2658, 111 (2003).
           <https://doi.org/10.1007/3-540-44862-4_13>`_

    .. [2] `M. Hochbruck and C. Lubich,
           SIAM Journal on Numerical Analysis 34, 1911 (1997).
           <https://doi.org/10.1137/S0036142995280572>`_
    """

    name = "estimated_krylov_subspace_dimension_arnoldi"
    args = [
        forge.arg("hamiltonian_sample", type=Union[np.array, coo_matrix, types.Tensor]),
        forge.arg(
            "lindblad_terms",
            type=List[Tuple[float, Union[np.array, coo_matrix, types.Tensor]]],
        ),
        forge.arg("duration", type=float),
        forge.arg("maximum_segment_duration", type=float),
        forge.arg("error_tolerance", type=float, default=1e-6),
        forge.arg("seed", type=Optional[int], default=None),
    ]
    rtype = types.Tensor

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        hamiltonian_sample = kwargs.get("hamiltonian_sample")
        lindblad_terms = kwargs.get("lindblad_terms")
        duration = kwargs.get("duration")
        maximum_segment_duration = kwargs.get("maximum_segment_duration")
        error_tolerance = kwargs.get("error_tolerance")

        check_operator(hamiltonian_sample, "hamiltonian_sample")
        check_lindblad_terms(lindblad_terms, hamiltonian_sample, "hamiltonian_sample")
        check_duration(duration, "duration")
        check_duration(maximum_segment_duration, "maximum_segment_duration")
        check_argument(
            error_tolerance > 0,
            "The error tolerance must be positive.",
            {"error_tolerance": error_tolerance},
        )

        return TensorNodeData(_operation, shape=())


class DensityMatrixEvolutionPwc(Node):
    r"""
    Calculates the state evolution of an open system described by the GKS-Lindblad master
    equation.

    The controls that you provide to this function have to be in piecewise constant
    format. If your controls are smooth sampleable tensor-valued functions (STFs), you
    have to discretize them with `discretize_stf` before passing them to this function.
    You may need to increase the number of segments that you choose for the
    discretization depending on the sizes of oscillations in the smooth controls.

    Parameters
    ----------
    initial_density_matrix : Union[np.ndarray, Tensor]
        A 2D array of the shape ``[D, D]`` representing the initial density matrix of
        the system, :math:`\rho_{\rm s}`. You can also pass a batch of density matrices
        and the input data shape must be ``[B, D, D]`` where ``B`` is the batch dimension.
    hamiltonian : Union[Pwc, SparsePwc]
        A piecewise-constant function representing the effective system Hamiltonian,
        :math:`H_{\rm s}(t)`, for the entire evolution duration. If you pass any Lindblad operator
        as a dense array, the Hamiltonian will get converted to a (dense) Pwc.
    lindblad_terms : List[Tuple[float, Union[np.ndarray, scipy.sparse.coo_matrix]]]
        A list of pairs, :math:`(\gamma_j, L_j)`, representing the positive decay rate
        :math:`\gamma_j` and the Lindblad operator :math:`L_j` for each coupling
        channel :math:`j`. If you pass the Hamiltonian as a Pwc, the operators will get
        converted to dense operators.
    sample_times : np.ndarray, optional
        A 1D array of length :math:`T` specifying the times :math:`\{t_i\}` at which this
        function calculates system states. Must be ordered and contain at least one element.
    krylov_subspace_dimension : Union[Tensor, int], optional
        The dimension of the Krylov subspace `k` for the Arnoldi method, which allows a more
        efficient calculation for large Hilbert spaces. A larger value leads to
        a better precision at the cost of longer computational time. If omitted or None
        it calculates the exact piecewise constant solution.

    name : str, optional
        The name of the node.

    Returns
    -------
    Tensor(complex)
        Systems states at sample times. The shape of the return value is ``[D, D]`` or
        ``[T, D, D]``, depending on whether you provide sample times.
        Otherwise, the shape is ``[B, T, D, D]`` if you provide a batch of initial states.

    See Also
    --------
    discretize_stf : Discretize an `Stf` into a `Pwc`.
    estimated_krylov_subspace_dimension_arnoldi : Obtain a Krylov subspace dimension to use
        with this integrator.
    sparse_pwc_operator : Create `SparsePwc` operators.
    state_evolution_pwc : Corresponding operation for coherent evolution.

    Notes
    -----
    Under Markovian approximation, the dynamics of an open quantum system can be described by
    the GKS-Lindblad master equation [1]_ [2]_

    .. math::
        \frac{{\rm d}\rho_{\rm s}(t)}{{\rm d}t} = -i [H_{\rm s}(t), \rho_{\rm s}(t)]
        + \sum_j \gamma_j {\mathcal D}[L_j] \rho_{\rm s}(t) \;,

    where :math:`{\mathcal D}` is a superoperator describing the decoherent process in the
    system evolution and defined as

    .. math::
        {\mathcal D}[X]\rho := X \rho X^\dagger
            - \frac{1}{2}\left( X^\dagger X \rho + \rho X^\dagger X \right)

    for any system operator :math:`X`. This function calculates the system state at the
    sample times :math:`t_j` that you provide.

    References
    ----------
    .. [1] `V. Gorini, A. Kossakowski, E. C. G. Sudarshan,
            Journal of Mathematical Physics 17, 821 (1976).
            <https://doi.org/10.1063/1.522979>`_
    .. [2] `G. Lindblad, Communications in Mathematical Physics 48, 119 (1976).
            <https://doi.org/10.1007/BF01608499>`_
    """
    name = "density_matrix_evolution_pwc"
    args = [
        forge.arg("initial_density_matrix", type=Union[types.Tensor, np.ndarray]),
        forge.arg("hamiltonian", type=Union[types.Pwc, types.SparsePwc]),
        forge.arg(
            "lindblad_terms", type=List[Tuple[float, Union[np.ndarray, coo_matrix]]]
        ),
        forge.arg("sample_times", type=Optional[np.ndarray], default=None),
        forge.arg(
            "krylov_subspace_dimension",
            type=Union[int, types.Tensor, None],
            default=None,
        ),
    ]
    rtype = types.Tensor

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        sample_times = kwargs.get("sample_times")
        initial_density_matrix = kwargs.get("initial_density_matrix")
        hamiltonian = kwargs.get("hamiltonian")
        lindblad_terms = kwargs.get("lindblad_terms")

        check_argument(
            isinstance(hamiltonian, (PwcNodeData, SparsePwcNodeData)),
            "Hamiltonian must be a Pwc or a SparsePwc.",
            {"hamiltonian": hamiltonian},
        )
        check_argument(
            isinstance(initial_density_matrix, (np.ndarray, TensorNodeData)),
            "Initial density matrix must be a NumPy array or a Tensor.",
            {"initial_density_matrix": initial_density_matrix},
        )
        if sample_times is not None:
            check_sample_times(sample_times, "sample_times")
        check_density_matrix_shape(initial_density_matrix, "initial_density_matrix")
        check_oqs_hamiltonian(hamiltonian, initial_density_matrix)
        check_lindblad_terms(
            lindblad_terms, initial_density_matrix, "initial_density_matrix"
        )

        initial_state_shape = initial_density_matrix.shape
        if sample_times is None:
            shape = initial_state_shape
        else:
            shape = (
                initial_state_shape[:-2]
                + (len(sample_times),)
                + initial_state_shape[-2:]
            )
        return TensorNodeData(_operation, shape=shape)
