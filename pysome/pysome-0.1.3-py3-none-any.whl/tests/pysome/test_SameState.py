import unittest
from collections import Hashable

from pysome import default_name, SameState, Same, SameOutsideExpect


class DefaultNameTest(unittest.TestCase):
    def test_basics(self):
        self.assertTrue(isinstance(default_name, Hashable))
        self.assertTrue(len({default_name, default_name}) == 1)


class SameStateTest(unittest.TestCase):
    def test_basics(self):
        self.assertTrue(set(SameState._state.keys()) == set(SameState._allow.keys()))

        for key in SameState._allow.keys():
            self.assertTrue(SameState._allow[key] is False)
            self.assertTrue(SameState._state[key] == {})

    def test_same_usage(self):
        same = Same()
        with self.assertRaises(SameOutsideExpect):
            _ = same == 12

        SameState._start()
        self.assertTrue(same == 12)
        self.assertTrue(same == 12)
        self.assertFalse(same == 13)
        SameState._end()
        with self.assertRaises(SameOutsideExpect):
            _ = same == 12
