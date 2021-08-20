import unittest
import pytest

import numpy as np
import pandas as pd


from feyn.metrics import get_pearson_correlations


class TestPearsonCorrelation(unittest.TestCase):

    def setUp(self):
        self.X = np.array([4, 3, 1, 5])
        self.y = np.array(["a", "a", "b", "b"])
    
    def test_works_with_np_dict(self):

        graph = FakeGraph(1)
        data = {
            'target': np.random.random(5),
            'x': np.random.random(5)
        }
        mutual = get_pearson_correlations(graph, data)
        assert mutual is not None


    def test_works_with_pd_dataframe(self):
        graph = FakeGraph(1.3)
        data = pd.DataFrame({
            'target': np.random.random(5),
            'x': np.random.random(5)
        })
        mutual = get_pearson_correlations(graph, data)
        assert mutual is not None



class FakeInteraction:

    def __init__(self, name):
        self.name = name
        self.activation = [0]

    def _query(self):
        self.activation = np.random.random(1)


class FakeGraph:
    interactions = [FakeInteraction('x'), FakeInteraction('target')]

    def __init__(self, addition):
        self.addition = addition

    def __getitem__(self, key):
        return self.interactions[key]

    def __iter__(self):
        return iter(self.interactions)

    def predict(self, derterfrerm):
        return derterfrerm['x'] + self.addition

    def _query(self,a,b):
        for i in self.interactions:
            i._query()
    
    def __len__(self):
        return len(self.interactions)