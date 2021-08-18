
import unittest
import uhepp

class OutsideTestCase(unittest.TestCase):
    """Check the code merging under- and overflow"""

    def test_output_values(self):
        """Check that under- and overflow bins are merged properly"""
        hist = uhepp.UHeppHist("x", [0, 10, 20, 30])
        hist.include_overflow = True
        hist.include_underflow = True
        hist.yields["main"] = uhepp.Yield([1, 2, 3, 4, 5])

        si = uhepp.StackItem(["main"], label="main")
        hist.stacks.append(uhepp.Stack([si], bartype='points'))
        fig, ax = hist.render()

        points = ax.lines[0]
        self.assertEqual(list(points.get_xdata()), [5, 15, 25])
        self.assertEqual(list(points.get_ydata()), [3, 3, 9])
