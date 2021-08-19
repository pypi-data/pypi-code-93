#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np


class PartonicVars:
    """Cache all partonic vars"""

    def __init__(self, xi, eta):
        self.xi = xi
        self.eta = eta
        self.rho_q = -4.0 / xi
        self.beta_q = np.sqrt(1.0 - self.rho_q)
        self.chi_q = (self.beta_q - 1.0) / (self.beta_q + 1.0)
        self.rho = 1.0 / (1.0 + eta)
        self.beta = np.sqrt(1.0 - self.rho)
        self.chi = (1.0 - self.beta) / (1.0 + self.beta)
