import unittest

import numpy as np
import pandas as pd
from numpy.testing import assert_array_equal

import feyn.tools

class TestTools(unittest.TestCase):
    def test_split(self):
        data = {
            "a": np.array(range(10)),
            "b": np.array(range(10))
        }

        with self.subTest("Can split dict of arrays"):
            s1, s2 = feyn.tools.split(data,ratio=[4,1])

            # We should get 8 out of 10 samples in the first bucket
            self.assertEqual(len(s1["a"]), 8)
            # Order is preserved across the columns
            assert_array_equal(s1["a"], s1["b"])


            # We should get 2 out of 10 samples in the second bucket
            self.assertEqual(len(s2["a"]), 2)
            assert_array_equal(s2["a"], s2["b"])

        with self.subTest("Can split pandas"):
            df = pd.DataFrame(data)
            s1, s2 = feyn.tools.split(df,ratio=[4,1])

            # We should get 8 out of 10 samples in the first bucket
            self.assertEqual(len(s1), 8)

            # We should get 2 out of 10 samples in the second bucket
            self.assertEqual(len(s2), 2)
