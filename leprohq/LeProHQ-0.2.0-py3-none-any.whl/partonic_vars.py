# -*- coding: utf-8 -*-

import numba as nb
import numpy as np


@nb.njit("UniTuple(f8,3)(f8)", cache=True)
def build_xi(xi):
    rho_q = -4.0 / xi
    beta_q = np.sqrt(1.0 - rho_q)
    chi_q = (beta_q - 1.0) / (beta_q + 1.0)
    return (rho_q, beta_q, chi_q)


@nb.njit("UniTuple(f8,3)(f8)", cache=True)
def build_eta(eta):
    rho = 1.0 / (1.0 + eta)
    beta = np.sqrt(1.0 - rho)
    chi = (1.0 - beta) / (1.0 + beta)
    return (rho, beta, chi)


@nb.njit("UniTuple(f8,3)(f8,f8)", cache=True)
def build_prime(xi, eta):
    # s' = s - q2 = s+Q2
    # 4m2/s' = 1/(s/4m2 + Q2/4m2) =  1/(1/(4m2/s) - 1/(4m2/q2))
    rho = 1.0 / (1.0 + eta)
    rho_q = -4.0 / xi
    rho_p = 1.0 / (1.0 / rho - 1.0 / rho_q)
    beta_p = np.sqrt(1.0 - rho_p)
    chi_p = (1.0 - beta_p) / (1.0 + beta_p)
    return (rho_p, beta_p, chi_p)
