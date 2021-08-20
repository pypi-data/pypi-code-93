import unittest
import pytest

import numpy as np
import pandas as pd

from feyn.metrics import calculate_mi, get_mutual_information


class TestMI(unittest.TestCase):

    def setUp(self):
        self.X = np.array([4, 3, 1, 5])
        self.y = np.array(["a", "a", "b", "b"])

    def test_mutual_information_np_array(self):
        actual = 0.6931471805599452
        pred = calculate_mi([self.X, self.y])

        self.assertEqual(pred, actual)

    def test_mutual_information_pd_series_num_ix_wo_0(self):
        ix = [1,2,3,4]
        df = pd.DataFrame({"X": self.X, "y" : self.y}, index = ix)        
        actual = 0.6931471805599452
        pred = calculate_mi([df.loc[:,"X"], df.loc[:,"y"]])
        self.assertEqual(pred,actual)

    def test_mutual_information_cont(self):
        np.random.seed(42)
        X = np.random.random((1000,))
        Y = np.random.random((1000,))
        pred = calculate_mi([X, Y], float_bins=3)
        self.assertAlmostEqual(pred, 0, places=2)