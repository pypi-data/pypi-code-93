import unittest
import pytest

import numpy as np
import pandas as pd

import _feyn
import feyn

from feyn._base_reporting_mixin import BaseReportingMixin


from feyn.metrics import get_mutual_information, calculate_mi
from feyn.metrics._metrics import _get_activations

class TestGetMI(unittest.TestCase):

    def setUp(self):
        self.addition = 5

        self.graph = FakeModel(self.addition)
        self.x = np.array([1,2,3,4])
        self.target = np.array([3,2,1,0])

    def testFakeModelActivations(self):

        data = {"x": self.x, "target": self.target}
        activations = _get_activations(self.graph, data)

        actual_act = np.array([ [1, 2, 3, 4 ],
                                [6, 7, 8, 9 ],
                                [3, 2, 1, 0 ] ])

        assert np.array_equal(activations, actual_act)


    def test_works_with_np_dict(self):

        data = {"x": self.x, "target": self.target}

        test_mi = get_mutual_information(self.graph, data)
        actual_mi = [calculate_mi([self.x, self.target]),
                    calculate_mi([self.x + self.addition, self.target]),
                    calculate_mi([self.target, self.target])]
        self.assertEqual(test_mi, actual_mi)


    def test_works_with_pd_dataframe(self):

        data = pd.DataFrame({"x": self.x, "target": self.target})

        test_mi = get_mutual_information(self.graph, data)
        actual_mi = [calculate_mi([self.x, self.target]),
                    calculate_mi([self.x + self.addition, self.target]),
                    calculate_mi([self.target, self.target])]

        self.assertEqual(test_mi, actual_mi)


class FakeInteraction:
    def __init__(self, name, addition = None):
        self.name = name
        if addition is not None:
            self.addition = addition

    def _query(self, row):
        if self.name == "x":
            self.activation = row["x"]
        if self.name == "add":
            self.activation = row["x"] + self.addition
        if self.name == "target":
            self.activation = row["target"]



class FakeModel(feyn.Model, BaseReportingMixin):


    def __init__(self, addition):
        self.addition = addition

        self.interactions = [FakeInteraction('x'),
                            FakeInteraction("add", addition),
                            FakeInteraction('target')]

    def __getitem__(self, key):
        return self.interactions[key]

    def __iter__(self):
        return iter(self.interactions)

    def predict(self, derterfrerm):
        return derterfrerm['x'] + self.addition

    def _query(self,row,b):
        for i in self.interactions:
            i._query(row)

    def __len__(self):
        return len(self.interactions)
