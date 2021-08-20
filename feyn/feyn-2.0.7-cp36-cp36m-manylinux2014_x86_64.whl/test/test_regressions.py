"""
This file contains regression errors observed in production. Some of these tests may
be a bit gnarly formulated, they may be a bit more fragile, and they probably do not
smell like a requirement specification for the feyn.

The idea is, that these can be deleted whenever they become too annoying.
"""

import unittest

import numpy as np

import feyn
import _feyn
from feyn import connect_qlattice


class TestMiscRegressions(unittest.TestCase):
    def test_model_handles_nans(self):
        in_reg = _feyn.Interaction("in:linear(f)->i", (0, -1, -1), name="in_reg")
        tanh = _feyn.Interaction("cell:tanh(i)->i", (0, 0, 0))
        out_reg = _feyn.Interaction("out:linear(i)->f", (1, -1, -1), name="out_reg")

        m = feyn.Model(3)
        m[0] = in_reg
        m[1] = tanh
        m[2] = out_reg

        tanh._set_source(0, 0)
        out_reg._set_source(0, 1)

        with self.subTest("ValueError when Nan in input"):
            with self.assertRaises(ValueError) as ctx:
                data = {"in_reg": [np.nan]}
                m.predict(data)

            self.assertIn("nan", str(ctx.exception))

        with self.subTest("ValueError when inf in input"):
            with self.assertRaises(ValueError) as ctx:
                data = {"in_reg": [np.inf]}
                m.predict(data)

            self.assertIn("inf", str(ctx.exception))

        with self.subTest("ValueError when Nan in output"):
            with self.assertRaises(ValueError) as ctx:
                data = {"in_reg": np.array([1.0]), "out_reg": np.array([np.nan])}
                m._fit(data, loss_function=feyn.losses.squared_error)

            self.assertIn("nan", str(ctx.exception))

    def test_filter_works_with_numpy_int(self):
        lt = connect_qlattice()
        lt.reset()
        models = lt.sample_models(["a", "b", "c"], "y", max_complexity=2)[:10]
        n2 = sum(map(lambda m: m.edge_count == 2, models))
        complexity_filter = feyn.filters.Complexity(np.int64(2))

        filtered_models = list(filter(complexity_filter, models))
        self.assertEqual(n2, len(filtered_models))
