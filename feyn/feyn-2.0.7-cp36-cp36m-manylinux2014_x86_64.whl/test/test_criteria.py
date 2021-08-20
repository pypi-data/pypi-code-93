import unittest
import numpy as np

import feyn
import warnings


class TestCriteria(unittest.TestCase):
    def test_aic_computes(self):
        loss_value = 1e4
        param_count = 10
        n_samples = 100

        aic = feyn.criteria.aic(loss_value, param_count, n_samples)

        self.assertAlmostEqual(aic == 901, 0)

    def test_bic_computes(self):
        loss_value = 1e4
        param_count = 10
        n_samples = 100

        bic = feyn.criteria.bic(loss_value, param_count, n_samples)

        self.assertAlmostEqual(bic, 967, 0)

    def test_outside_math_domain_of_log_computes(self):
        loss_value = 0
        param_count = 10
        n_samples = 100

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', r'divide by zero encountered in log')
            bic = feyn.criteria.bic(loss_value, param_count, n_samples)
            aic = feyn.criteria.aic(loss_value, param_count, n_samples)

        assert bic == -np.inf
        assert aic == -np.inf
