import unittest
import pytest
import sys

import pandas as pd
import numpy as np

from feyn.plots._graph_flow import plot_activation_flow
from ..test_sdk import _simple_unary_model


class TestPlotActivationFlow(unittest.TestCase):
    def setUp(self):
        self.model = _simple_unary_model()
        self.data = pd.DataFrame({"age": [1, 2, 3], "insurable": [0, 1, 1]})
        self.sample = pd.DataFrame({"age": [12], "insurable": [0]})

    def test_when_data_is_DataFrame(self):
        self.assertIsNotNone(plot_activation_flow(self.model, self.data, self.sample))

    def test_sample_is_Series(self):
        sample = pd.Series({"age": 5})
        self.assertIsNotNone(plot_activation_flow(self.model, self.data, sample))

    def test_passthrough(self):
        with self.subTest("No errors raised with normal use."):
            model = _simple_unary_model()
            data = get_dataframe()
            model.plot_flow(data, data.iloc[0:1])


@pytest.mark.skipif(sys.version_info < (3, 7), reason="requires python3.7 or higher")
class TestActivationFlowValidation(unittest.TestCase):
    def setUp(self):
        self.model = _simple_unary_model()
        self.data = get_dataframe()
        self.sample = self.data.iloc[0:1]

    def test_model_validation(self):
        with self.assertRaises(TypeError):
            model = {"banana": "phone"}
            plot_activation_flow(model, self.data, self.sample)

    def test_data_validation(self):
        with self.assertRaises(TypeError):
            data = {"lost": [4, 8, 15, 16, 23, 42]}
            plot_activation_flow(self.model, data, self.sample)

    def test_sample_validation(self):
        with self.assertRaises(TypeError):
            sample = {"x": 2, "y": 0.75, "cat": "e"}
            plot_activation_flow(self.model, self.data, sample)


def get_dataframe():
    return pd.DataFrame(
        {
            "age": reversed(np.arange(5)),
            "smoker": np.linspace(0.0, 1.0, 5),
            "children": [4, 5, 6, 5, 4],
            "insurable": [0, 1, 0, 1, 0],
        }
    )
