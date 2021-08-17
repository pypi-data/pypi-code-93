import unittest
import numpy as np
import pandas as pd

from helpsk import utility as hu


# noinspection PyMethodMayBeStatic
class TestValidation(unittest.TestCase):

    def test_is_debugging(self):
        # not sure how to test is_debugging is true, except manually
        assert not hu.is_debugging()
