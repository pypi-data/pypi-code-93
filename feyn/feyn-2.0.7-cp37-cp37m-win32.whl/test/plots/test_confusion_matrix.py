import unittest
import pytest
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from feyn.plots import plot_confusion_matrix
from ..test_sdk import _simple_binary_model


class TestConfusionMatrix(unittest.TestCase):
    def tearDown(self):
        plt.close()

    def test_bool_for_y_true(self):
        y_true = np.array([True, False])
        y_pred = np.array([1, 1])
        self.assertIsNotNone(plot_confusion_matrix(y_true, y_pred))

    def test_bool_for_y_pred(self):
        y_true = np.array([1, 0])
        y_pred = np.array([False, False])
        self.assertIsNotNone(plot_confusion_matrix(y_true, y_pred))

    def test_list_of_values_for_y_true_y_pred(self):
        y_true = [True, False]
        y_pred = [1, 1]
        self.assertIsNotNone(plot_confusion_matrix(y_true, y_pred))

    def test_passthrough(self):
        with self.subTest("No errors raised with normal use."):
            y_true = [True, False, True, False]
            y_pred = np.round([0.85, 0.46, 0.25, 0.5])
            plot_confusion_matrix(y_true, y_pred)
            model = _simple_binary_model()
            data = get_dataframe()
            model.plot_confusion_matrix(data)


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires python3.7 or higher")
class TestConfusionMatrixValidation(unittest.TestCase):
    def setUp(self):
        self.y_true = [True, False, True, False]
        self.y_pred = np.round([0.85, 0.46, 0.25, 0.5])

    def tearDown(self):
        plt.close()

    def test_y_validation(self):
        with self.assertRaises(TypeError):
            y_true = 1
            plot_confusion_matrix(y_true, self.y_pred)

        with self.assertRaises(TypeError):
            y_pred = 1
            plot_confusion_matrix(self.y_true, y_pred)

    def test_ax_validation(self):
        with self.assertRaises(TypeError):
            ax = plt.figure()
            plot_confusion_matrix(self.y_true, self.y_pred, ax=ax)

    def test_labels_validation(self):
        with self.assertRaises(TypeError):
            labels = 42
            plot_confusion_matrix(self.y_true, self.y_pred, labels=labels)


def get_dataframe():
    return pd.DataFrame(
        {
            "age": reversed(np.arange(5)),
            "smoker": np.linspace(0.0, 1.0, 5),
            "children": [4, 5, 6, 5, 4],
            "insurable": [0, 1, 0, 1, 0],
        }
    )
