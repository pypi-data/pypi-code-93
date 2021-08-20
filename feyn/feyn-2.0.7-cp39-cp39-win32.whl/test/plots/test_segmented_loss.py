import unittest
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import pytest

from feyn.reference import ConstantModel
from ..test_sdk import _simple_binary_model
from feyn.plots import plot_segmented_loss

class TestSegmentedLoss(unittest.TestCase):
    def setUp(self):
        self.model = _simple_binary_model()
        self.data = pd.DataFrame({
            "age": [1,2,3],
            "smoker": [0,0,1],
            "insurable": [0,1,1]
        })

    def tearDown(self):
        plt.close()

    def test_feyn_model(self):
        ax = plot_segmented_loss(self.model, self.data)
        self.assertIsNotNone(ax)

    def test_reference_model(self):
        model = ConstantModel("insurable", 1)
        ax = plot_segmented_loss(model, self.data)
        self.assertIsNotNone(ax)

class TestSegmentedLossValidation(unittest.TestCase):
    def setUp(self):
        self.model = _simple_binary_model()
        self.data = get_dataframe()

    def tearDown(self):
        plt.close()

    def test_by_validation(self):
        with self.subTest(
            "When `by` is not in data"
        ):
            with self.assertRaises(ValueError):
                by = 'banana'
                plot_segmented_loss(
                    self.model, self.data, by=by
                )

@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires python3.7 or higher")
class TestSegmentedLossTypeErrorValidation(unittest.TestCase):
    def setUp(self):
        self.model = _simple_binary_model()
        self.data = get_dataframe()

    def tearDown(self):
        plt.close()

    def test_passthrough(self):
        with self.subTest("No errors raised with normal use."):
            plot_segmented_loss(
                self.model, self.data
            )
            self.model.plot_segmented_loss(self.data)

    def test_model_validation(self):
        with self.assertRaises(TypeError):
            model = 'banana'
            plot_segmented_loss(
                model, self.data
            )

    def test_data_validation(self):
        with self.assertRaises(TypeError):
            data = {'banana': 'phone'}
            plot_segmented_loss(
                self.model, data
            )

    def test_by_validation(self):
        with self.subTest(
            "When `by` is not a string"
        ):
            with self.assertRaises(TypeError):
                by = 42
                plot_segmented_loss(
                    self.model, self.data, by=by
                )

    def test_ax_validation(self):
        with self.assertRaises(TypeError):
            ax = plt.figure()
            plot_segmented_loss(
                self.model, self.data, ax=ax
            )

def get_dataframe():
    return pd.DataFrame({
        'age': reversed(np.arange(5)),
        'smoker': np.linspace(0., 1., 5),
        "children": [4, 5, 6, 5, 4],
        'insurable': [0, 1, 0, 1, 0]
    })
