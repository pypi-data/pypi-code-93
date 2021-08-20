import unittest
import pytest

import numpy as np

from feyn.metrics._spearman import _rankdata

class TestSpear(unittest.TestCase):

    def test_rankdata(self):
        test_ls = np.array([10,14,14,6,7,7,12,7])
        actual = np.array([5. , 7.5, 7.5, 1. , 3. , 3. , 6. , 3. ])

        rnk_test_ls = _rankdata(test_ls)

        for i in range(len(test_ls)):
            assert rnk_test_ls[i] == actual[i]