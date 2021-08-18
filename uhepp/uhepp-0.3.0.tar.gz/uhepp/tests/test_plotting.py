
# Copyright (C) 2020 Frank Sauerburger

import unittest
from uhepp import UHeppHist, Stack, StackItem, Yield

class UHepPlotingTestCase(unittest.TestCase):
    """Check the implementation of various plotting methods"""

    def test_update_style_map(self):
        """Check that all allowed values are wired to the correct output"""
        kwds= {}
        UHeppHist._update_style(kwds, {"linewidth": 1.2,
                                      "linestyle": ':',
                                      "color": (1, 2, 3),
                                      "edgecolor": (2, 2, 3)})

        self.assertEqual(kwds, {"linewidth": 1.2,
                                "linestyle": ':',
                                "color": (1, 2, 3),
                                "edgecolor": (2, 2, 3)})


    def test_update_style_missing(self):
        """Check that missing input values keep the output unchanged"""
        kwds = {"linestyle": ':', "color": (1, 2, 3)}
        UHeppHist._update_style(kwds, {})
        self.assertEqual(kwds, {"linestyle": ':', "color": (1, 2, 3)})

    def test_update_style_aux(self):
        """Check that additional input values are ignored"""
        kwds = {}
        UHeppHist._update_style(kwds, {"linestyle": ":", "whatever": 3})
        self.assertEqual(kwds, {"linestyle": ':'})

    def test_no_uncertainty(self):
        """Check that plotting succeeds without uncertainties"""
        hist = UHeppHist("m", [100, 110, 120, 130, 140])
        hist.yields = {
            "a": Yield([  1,   2,   3,   4,   5,   6],
                       [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]),
            "b": Yield([  2,   3,   4,   3,   2,   1],
                       [0.4, 0.4, 0.5, 0.4, 0.5, 0.5]),
            "c": Yield([3.1, 3.2, 3.3, 3.4, 3.5, 3.6],
                       [0.1, 0.1, 0.1, 0.2, 0.2, 0.3]),
            "x": Yield([  6,   7,   8,   9,  10,  10],
                       [0.1, 0.1, 0.1, 0.2, 0.2, 0.3])
        }

        hist.stacks.append(Stack([
                StackItem(["a"], label="A"),
                StackItem(["b"], label="B"),
                StackItem(["c"], label="C"),
        ], error='no'))

        # Survival test
        hist.render()

    def test_no_stat_uncertainty(self):
        """Check that plotting succeeds without uncertainties"""
        hist = UHeppHist("m", [100, 110, 120, 130, 140])
        hist.yields = {
            "a": Yield([  1,   2,   3,   4,   5,   6]),
            "b": Yield([  2,   3,   4,   3,   2,   1]),
            "c": Yield([3.1, 3.2, 3.3, 3.4, 3.5, 3.6]),
            "x": Yield([  6,   7,   8,   9,  10,  10]),
        }

        hist.stacks.append(Stack([
                StackItem(["a"], label="A"),
                StackItem(["b"], label="B"),
                StackItem(["c"], label="C"),
        ]))

        # Survival test
        hist.render()
