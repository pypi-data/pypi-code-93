import unittest
import pytest
import sys
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

from feyn.plots._probability_plot import _pos_neg_classes
from feyn.plots._probability_plot import plot_probability_scores

from ..test_sdk import _simple_binary_model


class TestProbPlot(unittest.TestCase):
    def setUp(self):
        self.true = np.array([0, 1, 1, 0])
        self.pred = np.array([0.9, 0.3, 0.8, 0])

    def tearDown(self):
        plt.close()

    def test_pos_neg_classes(self):
        x, y = _pos_neg_classes(self.true, self.pred)
        assert (x == np.array([0.8, 0.3])).all()
        assert (y == np.array([0, 0.9])).all()

    def test_prob_scores(self):
        ax = plot_probability_scores(self.true, self.pred)

        assert ax is not None

    def test_axis(self):
        _, ax = plt.subplots()
        ax = plot_probability_scores(self.true, self.pred, ax=ax)
        assert ax is not None

    def test_validate_pred_list_of_floats(self):
        true = [1, 0, 0, 1]
        pred = [0.3, 0.1, 0.7, 0.99]

        ax = plot_probability_scores(true, pred)
        self.assertIsNotNone(ax)

    def test_passthrough(self):
        with self.subTest("No errors raised with normal use."):
            model = _simple_binary_model()
            model.predict = lambda data: [0.5] * len(data)
            data = get_dataframe()
            model.plot_probability_scores(data)


class TestProbabilityScoresValueErrorValidation(unittest.TestCase):
    def setUp(self):
        self.true = np.array([0, 1, 1, 0])
        self.pred = np.array([0.9, 0.3, 0.8, 0])

    def tearDown(self):
        plt.close()

    def test_valid_ytrue(self):
        true = [1, 2, 3, 4]
        with self.assertRaises(ValueError):
            plot_probability_scores(true, self.pred)

    def test_valid_same_lengths(self):
        true = [0, 1, 1]
        with self.assertRaises(ValueError):
            plot_probability_scores(true, self.pred)


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires python3.7 or higher")
class TestProbabilityScoresTypeErrorValidation(unittest.TestCase):
    def setUp(self):
        self.true = np.array([0, 1, 1, 0])
        self.pred = np.array([0.9, 0.3, 0.8, 0])

    def tearDown(self):
        plt.close()

    def test_iterable_of_floats_pred(self):
        pred = "hello"
        with self.assertRaises(TypeError):
            plot_probability_scores(self.true, pred)

    def test_iterable_of_floats_true(self):
        true = 23
        with self.assertRaises(TypeError):
            plot_probability_scores(true, self.pred)

    def test_axes_validation(self):
        fig = plt.figure()
        with self.assertRaises(TypeError):
            plot_probability_scores(self.true, self.pred, ax=fig)

    def test_nbins_validation(self):
        nbins = 1.5
        with self.assertRaises(TypeError):
            plot_probability_scores(self.true, self.pred, nbins=nbins)


def get_dataframe():
    return pd.DataFrame(
        {
            "age": reversed(np.arange(5)),
            "smoker": np.linspace(0.0, 1.0, 5),
            "children": [4, 5, 6, 5, 4],
            "insurable": [0, 1, 0, 1, 0],
        }
    )
