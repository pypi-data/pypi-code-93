# Copyright 2021 CR.Sparse Development Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import NamedTuple

import jax.numpy as jnp
from jax import vmap, jit, lax

from .util import abs_max_idx, gram_chol_update
from cr.sparse.la import solve_spd_chol
from .defs import RecoverySolution

class OMPState(NamedTuple):
    # The non-zero values
    x_I: jnp.ndarray
    """Non-zero values"""
    I: jnp.ndarray
    """The support for non-zero values"""
    Phi_I: jnp.array
    """Selected atoms"""
    L : jnp.array
    """ Cholesky factor """
    r: jnp.ndarray
    """The residuals"""
    r_norm_sqr: jnp.ndarray
    """The residual norm squared"""
    iterations: int
    """The number of iterations it took to complete"""


def solve(Phi, y, K, max_iters=None, res_norm_rtol=1e-4):
    """Solves the recovery/approximation problem :math:`y = \Phi x + e` using Orthogonal Matching Pursuit
    """
    # initialize residual
    r = y
    M = Phi.shape[0]
    N = Phi.shape[1]
    K = max_iters
    # squared norm of the signal
    y_norm_sqr = y.T @ y

    max_r_norm_sqr = y_norm_sqr * (res_norm_rtol ** 2) 

    if max_iters is None:
        max_iters = M

    # The proxy representation
    p = Phi.T @ y

    def init():
        # First correlation of residual with signal
        h = p
        # Index of best match
        i = abs_max_idx(h)
        # Initialize the array of selected indices
        I = jnp.array([i])
        # First matched atom
        phi_i = Phi[:, i]
        # Initial subdictionary of selected atoms
        Phi_I = jnp.expand_dims(phi_i, axis=1)
        # Initial L for Cholesky factorization of Gram matrix
        L = jnp.ones((1,1))
        # sub-vector of proxy corresponding to selected indices
        p_I = p[I]
        # sub-vector of representation coefficients estimated so far
        x_I = p_I
        # updated residual after first iteration
        r = y - Phi_I @ x_I
        # norm squared of new residual
        r_norm_sqr = r.T @ r
        return OMPState(x_I=x_I, I=I, Phi_I=Phi_I, L=L, r=r, r_norm_sqr=r_norm_sqr, iterations=1)

    def iteration(state):
        # conduct OMP iterations
        # compute the correlations
        h = Phi.T @ state.r
        # Index of best match
        i = abs_max_idx(h)
        # Update the set of indices
        I = jnp.append(state.I, i)
        # best matching atom
        phi_i = Phi[:, i]
        # Correlate with previously selected atoms
        v = state.Phi_I.T @ phi_i
        # Update the Cholesky factorization
        L = gram_chol_update(state.L, v)
        # Update the subdictionary
        Phi_I = jnp.hstack((state.Phi_I, jnp.expand_dims(phi_i,1)))
        # sub-vector of proxy corresponding to selected indices
        p_I = p[I]
        # sub-vector of representation coefficients estimated so far
        x_I = solve_spd_chol(L, p_I)
        # updated residual after first iteration
        r = y - Phi_I @ x_I
        # norm squared of new residual
        r_norm_sqr = r.T @ r
        return OMPState(x_I=x_I, I=I, Phi_I=Phi_I, L=L, r=r, r_norm_sqr=r_norm_sqr, iterations=1)

    def cond(state):
        # limit on residual norm 
        a = state.r_norm_sqr > max_r_norm_sqr
        # limit on number of iterations
        b = state.iterations < max_iters
        c = jnp.logical_and(a, b)
        return c

    state = lax.while_loop(cond, iteration, init())

    return RecoverySolution(x_I=state.x_I, I=state.I, r=state.r, 
        r_norm_sqr=state.r_norm_sqr, iterations=state.iterations)


solve_multi = vmap(solve, (None, 1, None, None, None), 0)
"""Solves the recovery/approximation problem :math:`Y = \Phi X + E` using Orthogonal Matching Pursuit

Extends :py:func:`cr.sparse.pursuit.omp.solve` using :py:func:`jax.vmap`.
"""

solve_jit = jit(solve, static_argnums=(2), static_argnames=("max_iters", "res_norm_rtol"))