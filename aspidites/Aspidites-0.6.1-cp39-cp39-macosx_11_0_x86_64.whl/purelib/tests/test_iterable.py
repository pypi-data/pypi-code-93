import unittest
from collections.abc import Iterable

from Aspidites._vendor import HEAD, TAIL, MatchError, match_iterable as mi
from Aspidites._vendor import ANY


class IterableTests(unittest.TestCase):

    def setUp(self):
        # So we can wrap it later
        self.mi = mi

    def test_match_iterable(self):
        self.assertEqual(self.mi([1, 2, 3], [1, 2, 3]), (True, []))
        self.assertEqual(self.mi([str, str], ["hello", "world"]), (True, ["hello", "world"]))
        self.assertEqual(self.mi([1, 2], [1, 3]), (False, []))

        self.assertEqual(self.mi([1, 2], [1]), (False, []))

    def test_match_iterable_with_a_value(self):
        self.assertEqual(self.mi([1, 2], 33), (False, []))
        self.assertEqual(self.mi(33, [1, 2]), (False, []))

    def test_match_iterable_underscore(self):
        self.assertEqual(self.mi([1, ANY, 3], [1, 2, 3]), (True, [2]))
        self.assertEqual(self.mi([1, ANY, ANY], [1, 2, 3]), (True, [2, 3]))
        self.assertEqual(self.mi([ANY, 2, ANY], [1, 2, 3]), (True, [1, 3]))

    def test_match_iterable_pattern_longer_than_var(self):
        self.assertEqual(self.mi([ANY, ANY, ANY], [1, 2]), (False, []))
        self.assertEqual(self.mi([ANY, 2, ANY], [1, 2]), (False, []))

    def test_match_iterable_nested(self):
        self.assertEqual(self.mi([1, [2, 3]], [1, [2, 3]]), (True, []))
        self.assertEqual(self.mi([1, [2, ANY]], [1, [2, 3]]), (True, [3]))
        self.assertEqual(self.mi([1, [2, ANY], ANY],
                                 [1, [2, 3], 4]), (True, [3, 4]))
        self.assertEqual(self.mi([1, [2, [ANY, 4], ANY], ANY],
                                 [1, [2, [3, 4], 5], 6]), (True, [3, 5, 6]))

    def test_match_iterable_basic_HEAD(self):
        self.assertEqual(self.mi([HEAD], [1]),   (True, [1]))
        self.assertEqual(self.mi([HEAD], []),    (False, []))

    def test_match_iterable_HEAD(self):
        self.assertEqual(self.mi([HEAD, 2], [1, 2]), (True, [1]))
        self.assertEqual(self.mi([HEAD, ANY], [1, 2]), (True, [1, 2]))

    def test_match_iterable_TAIL(self):
        self.assertEqual(self.mi([TAIL],         [1, 2, 3]), (True, [[1, 2, 3]]))
        self.assertEqual(self.mi([ANY, TAIL],      [1, 2, 3]), (True, [1, [2, 3]]))
        self.assertEqual(self.mi([ANY, ANY, TAIL],   [1, 2, 3]), (True, [1, 2, [3]]))

        self.assertEqual(self.mi([ANY, TAIL],      [1]),       (True, [1, []]))
        self.assertEqual(self.mi([ANY, TAIL],      [1, 2]),    (True, [1, [2]]))
        self.assertEqual(self.mi([ANY, ANY, TAIL],   [1, 2]),    (True, [1, 2, []]))

    def test_match_iterable_HEAD_TAIL(self):
        self.assertEqual(self.mi([HEAD, TAIL], [1, 2, 3]),   (True, [1, [2, 3]]))
        self.assertEqual(self.mi([HEAD, TAIL], [1]),         (True, [1, []]))
        self.assertEqual(self.mi([HEAD, TAIL], []),          (False, []))

    def test_match_iterable_HEAD_should_be_in_first_position(self):
        with self.assertRaises(MatchError):
            self.mi([1, HEAD], [1, 2])

        with self.assertRaises(MatchError):
            self.mi([1, HEAD, 3], [1, 2, 3])

    def test_match_iterable_TAIL_should_be_in_last_position(self):
        with self.assertRaises(MatchError):
            self.mi([1, TAIL, 3], [1, 2, 3])

        with self.assertRaises(MatchError):
            self.mi([TAIL, 2], [1, 2, 3])

    def test_match_iterable_with_tuples(self):
        def convert_to_tuples(patterns, values):
            patterns = tuple(patterns) if isinstance(patterns, Iterable) else patterns
            values = tuple(values) if isinstance(values, Iterable) else values
            return mi(patterns, values)

        self.mi = convert_to_tuples

        methods = [f for f in dir(self) if callable(getattr(self, f))
                   if f.startswith('test_') and f != 'test_match_iterable_with_tuples']

        for method in methods:
            getattr(self, method)()

        self.mi = mi
