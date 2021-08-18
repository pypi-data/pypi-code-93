
import math
import unittest
import uhepp

class UncertaintyTestCase(unittest.TestCase):
    """Test the uncertainty computation"""

    def assertListAlmostEqual(self, a, b, *args, **kwds):
        for A, B in zip(a, b):
            self.assertAlmostEqual(A, B, *args, **kwds)
        self.assertEqual(len(a), len(b), *args, **kwds)


    def test_stat_default(self):
        """Check the uncertainty of a standard case"""
        hist = uhepp.UHeppHist("m", [100, 110, 120, 130, 140])
        hist.yields = {
            "a": uhepp.Yield([  1,   2,   3,   4,   5,   6],
                             [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]),
            "b": uhepp.Yield([  2,   3,   4,   3,   2,   1],
                             [0.4, 0.4, 0.5, 0.4, 0.5, 0.5]),
            "c": uhepp.Yield([3.1, 3.2, 3.3, 3.4, 3.5, 3.6],
                             [0.1, 0.1, 0.1, 0.2, 0.2, 0.3]),
            "x": uhepp.Yield([  6,   7,   8,   9,  10,  10],
                             [0.1, 0.1, 0.1, 0.2, 0.2, 0.3])
        }

        hist.stacks.append(uhepp.Stack([
                uhepp.StackItem(["a"], label="A"),
                uhepp.StackItem(["b"], label="B"),
                uhepp.StackItem(["c"], label="C"),
        ]))
        hist.stacks.append(uhepp.Stack([
                uhepp.StackItem(["x"], label="Data"),
        ], bartype="points"))

        fig, ax = hist.render()
    
        # A polygon
        self.assertEqual(list(ax.patches[0].xy[ 0]), [100, 0])
        self.assertEqual(list(ax.patches[0].xy[ 1]), [100, 2])
        self.assertEqual(list(ax.patches[0].xy[ 2]), [110, 2])
        self.assertEqual(list(ax.patches[0].xy[ 3]), [110, 3])
        self.assertEqual(list(ax.patches[0].xy[ 4]), [120, 3])
        self.assertEqual(list(ax.patches[0].xy[ 5]), [120, 4])
        self.assertEqual(list(ax.patches[0].xy[ 6]), [130, 4])
        self.assertEqual(list(ax.patches[0].xy[ 7]), [130, 5])
        self.assertEqual(list(ax.patches[0].xy[ 8]), [140, 5])
        self.assertEqual(list(ax.patches[0].xy[ 9]), [140, 0])
        self.assertEqual(list(ax.patches[0].xy[10]), [130, 0])
        self.assertEqual(list(ax.patches[0].xy[11]), [130, 0])
        self.assertEqual(list(ax.patches[0].xy[12]), [120, 0])
        self.assertEqual(list(ax.patches[0].xy[13]), [120, 0])
        self.assertEqual(list(ax.patches[0].xy[14]), [110, 0])
        self.assertEqual(list(ax.patches[0].xy[15]), [110, 0])
        self.assertEqual(list(ax.patches[0].xy[16]), [100, 0])
        self.assertEqual(len(ax.patches[0].xy), 17)
    
        # B polygon
        self.assertEqual(list(ax.patches[1].xy[ 0]), [100, 2])
        self.assertEqual(list(ax.patches[1].xy[ 1]), [100, 5])
        self.assertEqual(list(ax.patches[1].xy[ 2]), [110, 5])
        self.assertEqual(list(ax.patches[1].xy[ 3]), [110, 7])
        self.assertEqual(list(ax.patches[1].xy[ 4]), [120, 7])
        self.assertEqual(list(ax.patches[1].xy[ 5]), [120, 7])
        self.assertEqual(list(ax.patches[1].xy[ 6]), [130, 7])
        self.assertEqual(list(ax.patches[1].xy[ 7]), [130, 7])
        self.assertEqual(list(ax.patches[1].xy[ 8]), [140, 7])
        self.assertEqual(list(ax.patches[1].xy[ 9]), [140, 5])
        self.assertEqual(list(ax.patches[1].xy[10]), [130, 5])
        self.assertEqual(list(ax.patches[1].xy[11]), [130, 4])
        self.assertEqual(list(ax.patches[1].xy[12]), [120, 4])
        self.assertEqual(list(ax.patches[1].xy[13]), [120, 3])
        self.assertEqual(list(ax.patches[1].xy[14]), [110, 3])
        self.assertEqual(list(ax.patches[1].xy[15]), [110, 2])
        self.assertEqual(list(ax.patches[1].xy[16]), [100, 2])
        self.assertEqual(len(ax.patches[1].xy), 17)
    
        # C polygon
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 0]), [100,    5])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 1]), [100,  8.2])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 2]), [110,  8.2])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 3]), [110, 10.3])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 4]), [120, 10.3])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 5]), [120, 10.4])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 6]), [130, 10.4])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 7]), [130, 10.5])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 8]), [140, 10.5])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 9]), [140,    7])
        self.assertListAlmostEqual(list(ax.patches[2].xy[10]), [130,    7])
        self.assertListAlmostEqual(list(ax.patches[2].xy[11]), [130,    7])
        self.assertListAlmostEqual(list(ax.patches[2].xy[12]), [120,    7])
        self.assertListAlmostEqual(list(ax.patches[2].xy[13]), [120,    7])
        self.assertListAlmostEqual(list(ax.patches[2].xy[14]), [110,    7])
        self.assertListAlmostEqual(list(ax.patches[2].xy[15]), [110,    5])
        self.assertListAlmostEqual(list(ax.patches[2].xy[16]), [100,    5])
        self.assertEqual(len(ax.patches[2].xy), 17)
    
        # Error band
        self.assertEqual(ax.patches[3]._x0, 100)
        self.assertEqual(ax.patches[3]._width, 10)

        self.assertAlmostEqual(ax.patches[3]._height**2 / 4,
                               0.2**2 + 0.4**2 + 0.1**2)
        self.assertAlmostEqual(2 * ax.patches[3]._y0 + ax.patches[3]._height, 8.2 * 2)

        self.assertEqual(ax.patches[4]._x0, 110)
        self.assertEqual(ax.patches[3]._width, 10)
        self.assertAlmostEqual(ax.patches[4]._height**2 / 4,
                               0.3**2 + 0.5**2 + 0.1**2)
        self.assertAlmostEqual(2 * ax.patches[4]._y0 + ax.patches[4]._height, 10.3 * 2)

        self.assertEqual(ax.patches[5]._x0, 120)
        self.assertEqual(ax.patches[3]._width, 10)
        self.assertAlmostEqual(ax.patches[5]._height**2 / 4,
                               0.4**2 + 0.4**2 + 0.2**2)
        self.assertAlmostEqual(2 * ax.patches[5]._y0 + ax.patches[5]._height, 10.4 * 2)

        self.assertEqual(ax.patches[6]._x0, 130)
        self.assertEqual(ax.patches[3]._width, 10)
        self.assertAlmostEqual(ax.patches[6]._height**2 / 4,
                               0.5**2 + 0.5**2 + 0.2**2)
        self.assertAlmostEqual(2 * ax.patches[6]._y0 + ax.patches[6]._height, 10.5 * 2)

        # X points
        self.assertEqual(list(ax.lines[0].get_xdata()), [105, 115, 125, 135])
        self.assertEqual(list(ax.lines[0].get_ydata()), [7, 8, 9, 10])


        # X error
        self.assertEqual(list(ax.lines[0].get_xdata()), [105, 115, 125, 135])
        self.assertEqual(list(ax.lines[0].get_ydata()), [7, 8, 9, 10])
        self.assertEqual(len(ax.lines), 1)

        vertical = ax.containers[1][2][1].get_segments()
        self.assertEqual(list(vertical[0][0]), [105, 6.9])
        self.assertEqual(list(vertical[0][1]), [105, 7.1])
        self.assertEqual(list(vertical[1][0]), [115, 7.9])
        self.assertEqual(list(vertical[1][1]), [115, 8.1])
        self.assertEqual(list(vertical[2][0]), [125, 8.8])
        self.assertEqual(list(vertical[2][1]), [125, 9.2])
        self.assertEqual(list(vertical[3][0]), [135, 9.8])
        self.assertEqual(list(vertical[3][1]), [135, 10.2])
        self.assertEqual(len(vertical), 4)

        horizontal = ax.containers[1][2][0].get_segments()
        self.assertEqual(list(horizontal[0][0]), [100, 7])
        self.assertEqual(list(horizontal[0][1]), [110, 7])
        self.assertEqual(list(horizontal[1][0]), [110, 8])
        self.assertEqual(list(horizontal[1][1]), [120, 8])
        self.assertEqual(list(horizontal[2][0]), [120, 9])
        self.assertEqual(list(horizontal[2][1]), [130, 9])
        self.assertEqual(list(horizontal[3][0]), [130, 10])
        self.assertEqual(list(horizontal[3][1]), [140, 10])
        self.assertEqual(len(horizontal), 4)


    def test_stat_single_si(self):
        """With a single stack item using multiple yields"""
        hist = uhepp.UHeppHist("m", [100, 110, 120, 130, 140])
        hist.yields = {
            "a": uhepp.Yield([  1,   2,   3,   4,   5,   6],
                             [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]),
            "b": uhepp.Yield([  2,   3,   4,   3,   2,   1],
                             [0.4, 0.4, 0.5, 0.4, 0.5, 0.5]),
            "c": uhepp.Yield([3.1, 3.2, 3.3, 3.4, 3.5, 3.6],
                             [0.1, 0.1, 0.1, 0.2, 0.2, 0.3]),
            "x": uhepp.Yield([  6,   7,   8,   9,  10,  10],
                             [0.1, 0.1, 0.1, 0.2, 0.2, 0.3])
        }

        hist.stacks.append(uhepp.Stack([
                uhepp.StackItem(["a", "b", "c"], label="A, B, C"),
        ]))
        hist.stacks.append(uhepp.Stack([
                uhepp.StackItem(["x"], label="Data"),
        ], bartype="points"))

        fig, ax = hist.render()
    
        # A polygon
        self.assertListAlmostEqual(list(ax.patches[0].xy[ 0]), [100,    0])
        self.assertListAlmostEqual(list(ax.patches[0].xy[ 1]), [100,  8.2])
        self.assertListAlmostEqual(list(ax.patches[0].xy[ 2]), [110,  8.2])
        self.assertListAlmostEqual(list(ax.patches[0].xy[ 3]), [110, 10.3])
        self.assertListAlmostEqual(list(ax.patches[0].xy[ 4]), [120, 10.3])
        self.assertListAlmostEqual(list(ax.patches[0].xy[ 5]), [120, 10.4])
        self.assertListAlmostEqual(list(ax.patches[0].xy[ 6]), [130, 10.4])
        self.assertListAlmostEqual(list(ax.patches[0].xy[ 7]), [130, 10.5])
        self.assertListAlmostEqual(list(ax.patches[0].xy[ 8]), [140, 10.5])
        self.assertListAlmostEqual(list(ax.patches[0].xy[ 9]), [140, 0])
        self.assertListAlmostEqual(list(ax.patches[0].xy[10]), [130, 0])
        self.assertListAlmostEqual(list(ax.patches[0].xy[11]), [130, 0])
        self.assertListAlmostEqual(list(ax.patches[0].xy[12]), [120, 0])
        self.assertListAlmostEqual(list(ax.patches[0].xy[13]), [120, 0])
        self.assertListAlmostEqual(list(ax.patches[0].xy[14]), [110, 0])
        self.assertListAlmostEqual(list(ax.patches[0].xy[15]), [110, 0])
        self.assertListAlmostEqual(list(ax.patches[0].xy[16]), [100, 0])
        self.assertEqual(len(ax.patches[0].xy), 17)

        # Error band
        self.assertEqual(ax.patches[1]._x0, 100)
        self.assertEqual(ax.patches[1]._width, 10)
        self.assertAlmostEqual(ax.patches[1]._height**2 / 4,
                               0.2**2 + 0.4**2 + 0.1**2)
        self.assertAlmostEqual(2 * ax.patches[1]._y0 + ax.patches[1]._height, 8.2 * 2)

        self.assertEqual(ax.patches[2]._x0, 110)
        self.assertEqual(ax.patches[2]._width, 10)
        self.assertAlmostEqual(ax.patches[2]._height**2 / 4,
                               0.3**2 + 0.5**2 + 0.1**2)
        self.assertAlmostEqual(2 * ax.patches[2]._y0 + ax.patches[2]._height, 10.3 * 2)

        self.assertEqual(ax.patches[3]._x0, 120)
        self.assertEqual(ax.patches[3]._width, 10)
        self.assertAlmostEqual(ax.patches[3]._height**2 / 4,
                               0.4**2 + 0.4**2 + 0.2**2)
        self.assertAlmostEqual(2 * ax.patches[3]._y0 + ax.patches[3]._height, 10.4 * 2)

        self.assertEqual(ax.patches[4]._x0, 130)
        self.assertEqual(ax.patches[4]._width, 10)
        self.assertAlmostEqual(ax.patches[4]._height**2 / 4,
                               0.5**2 + 0.5**2 + 0.2**2)
        self.assertAlmostEqual(2 * ax.patches[4]._y0 + ax.patches[4]._height, 10.5 * 2)


    def test_stat_rebin(self):
        """Check that uncertainty in a r3binned case"""
        hist = uhepp.UHeppHist("m", [100, 110, 120, 130, 140])
        hist.yields = {
            "a": uhepp.Yield([  1,   2,   3,   4,   5,   6],
                             [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]),
            "b": uhepp.Yield([  2,   3,   4,   3,   2,   1],
                             [0.4, 0.4, 0.5, 0.4, 0.5, 0.5]),
            "c": uhepp.Yield([3.1, 3.2, 3.3, 3.4, 3.5, 3.6],
                             [0.1, 0.1, 0.1, 0.2, 0.2, 0.3]),
            "x": uhepp.Yield([  6,   7,   8,   9,  10,  10],
                             [0.1, 0.1, 0.1, 0.2, 0.2, 0.3])
        }

        hist.stacks.append(uhepp.Stack([
                uhepp.StackItem(["a"], label="A"),
                uhepp.StackItem(["b"], label="B"),
                uhepp.StackItem(["c"], label="C"),
        ]))
        hist.stacks.append(uhepp.Stack([
                uhepp.StackItem(["x"], label="Data"),
        ], bartype="points"))
        hist.rebin_edges = [100, 120, 140]

        fig, ax = hist.render()
    
        # A polygon
        self.assertEqual(list(ax.patches[0].xy[0]), [100, 0])
        self.assertEqual(list(ax.patches[0].xy[1]), [100, 5])
        self.assertEqual(list(ax.patches[0].xy[2]), [120, 5])
        self.assertEqual(list(ax.patches[0].xy[3]), [120, 9])
        self.assertEqual(list(ax.patches[0].xy[4]), [140, 9])
        self.assertEqual(list(ax.patches[0].xy[5]), [140, 0])
        self.assertEqual(list(ax.patches[0].xy[6]), [120, 0])
        self.assertEqual(list(ax.patches[0].xy[7]), [120, 0])
        self.assertEqual(list(ax.patches[0].xy[8]), [100, 0])
        self.assertEqual(len(ax.patches[0].xy), 9)
    
        # B polygon
        self.assertEqual(list(ax.patches[1].xy[0]), [100, 5])
        self.assertEqual(list(ax.patches[1].xy[1]), [100, 12])
        self.assertEqual(list(ax.patches[1].xy[2]), [120, 12])
        self.assertEqual(list(ax.patches[1].xy[3]), [120, 14])
        self.assertEqual(list(ax.patches[1].xy[4]), [140, 14])
        self.assertEqual(list(ax.patches[1].xy[5]), [140, 9])
        self.assertEqual(list(ax.patches[1].xy[6]), [120, 9])
        self.assertEqual(list(ax.patches[1].xy[7]), [120, 5])
        self.assertEqual(list(ax.patches[1].xy[8]), [100, 5])
        self.assertEqual(len(ax.patches[1].xy), 9)
    
        # C polygon
        self.assertEqual(list(ax.patches[2].xy[0]), [100, 12])
        self.assertEqual(list(ax.patches[2].xy[1]), [100, 18.5])
        self.assertEqual(list(ax.patches[2].xy[2]), [120, 18.5])
        self.assertEqual(list(ax.patches[2].xy[3]), [120, 20.9])
        self.assertEqual(list(ax.patches[2].xy[4]), [140, 20.9])
        self.assertEqual(list(ax.patches[2].xy[5]), [140, 14])
        self.assertEqual(list(ax.patches[2].xy[6]), [120, 14])
        self.assertEqual(list(ax.patches[2].xy[7]), [120, 12])
        self.assertEqual(list(ax.patches[2].xy[8]), [100, 12])
        self.assertEqual(len(ax.patches[2].xy), 9)
    
        # Error band
        self.assertEqual(ax.patches[3]._x0, 100)
        self.assertEqual(ax.patches[3]._width, 20)

        self.assertAlmostEqual(ax.patches[3]._height**2 / 4,
            0.2**2 + 0.3**2 + 0.4**2 + 0.5**2 + 0.1**2 + 0.1**2)
        self.assertAlmostEqual(2 * ax.patches[3]._y0 + ax.patches[3]._height,
                               18.5 * 2)

        self.assertEqual(ax.patches[4]._x0, 120)
        self.assertEqual(ax.patches[4]._width, 20)
        self.assertAlmostEqual(ax.patches[4]._height**2 / 4,
            0.4**2 + 0.5**2 + 0.5**2 + 0.4**2 + 0.2**2 + 0.2**2)
        self.assertAlmostEqual(2 * ax.patches[4]._y0 + ax.patches[4]._height,
                               20.9 * 2)

        # X points
        self.assertEqual(list(ax.lines[0].get_xdata()), [110, 130])
        self.assertEqual(list(ax.lines[0].get_ydata()), [15, 19])
        self.assertEqual(len(ax.lines), 1)

        # X error
        sqrt2 = math.sqrt(2)
        sqrt8 = math.sqrt(8)
        vertical = ax.containers[1][2][1].get_segments()
        self.assertListAlmostEqual(list(vertical[0][0]), [110, 15 - 0.1 * sqrt2])
        self.assertListAlmostEqual(list(vertical[0][1]), [110, 15 + 0.1 * sqrt2])
        self.assertListAlmostEqual(list(vertical[1][0]), [130, 19 - 0.1 * sqrt8])
        self.assertListAlmostEqual(list(vertical[1][1]), [130, 19 + 0.1 * sqrt8])
        self.assertEqual(len(vertical), 2)

        horizontal = ax.containers[1][2][0].get_segments()
        self.assertEqual(list(horizontal[0][0]), [100, 15])
        self.assertEqual(list(horizontal[0][1]), [120, 15])
        self.assertEqual(list(horizontal[1][0]), [120, 19])
        self.assertEqual(list(horizontal[1][1]), [140, 19])
        self.assertEqual(len(horizontal), 2)

    def test_stat_outside(self):
        """Check that uncertainty when outside bins are merged"""
        hist = uhepp.UHeppHist("m", [100, 110, 120, 130, 140])
        hist.yields = {
            "a": uhepp.Yield([  1,   2,   3,   4,   5,   6],
                             [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]),
            "b": uhepp.Yield([  2,   3,   4,   3,   2,   1],
                             [0.4, 0.4, 0.5, 0.4, 0.5, 0.5]),
            "c": uhepp.Yield([3.1, 3.2, 3.3, 3.4, 3.5, 3.6],
                             [0.1, 0.1, 0.1, 0.2, 0.2, 0.3]),
            "x": uhepp.Yield([  6,   7,   8,   9,  10,  10],
                             [0.1, 0.1, 0.1, 0.2, 0.2, 0.3])
        }

        hist.stacks.append(uhepp.Stack([
                uhepp.StackItem(["a"], label="A"),
                uhepp.StackItem(["b"], label="B"),
                uhepp.StackItem(["c"], label="C"),
        ]))
        hist.stacks.append(uhepp.Stack([
                uhepp.StackItem(["x"], label="Data"),
        ], bartype="points"))

        hist.include_overflow = True
        hist.include_underflow = True

        fig, ax = hist.render()
    
        # A polygon
        self.assertEqual(list(ax.patches[0].xy[ 0]), [100, 0])
        self.assertEqual(list(ax.patches[0].xy[ 1]), [100, 3])
        self.assertEqual(list(ax.patches[0].xy[ 2]), [110, 3])
        self.assertEqual(list(ax.patches[0].xy[ 3]), [110, 3])
        self.assertEqual(list(ax.patches[0].xy[ 4]), [120, 3])
        self.assertEqual(list(ax.patches[0].xy[ 5]), [120, 4])
        self.assertEqual(list(ax.patches[0].xy[ 6]), [130, 4])
        self.assertEqual(list(ax.patches[0].xy[ 7]), [130, 11])
        self.assertEqual(list(ax.patches[0].xy[ 8]), [140, 11])
        self.assertEqual(list(ax.patches[0].xy[ 9]), [140, 0])
        self.assertEqual(list(ax.patches[0].xy[10]), [130, 0])
        self.assertEqual(list(ax.patches[0].xy[11]), [130, 0])
        self.assertEqual(list(ax.patches[0].xy[12]), [120, 0])
        self.assertEqual(list(ax.patches[0].xy[13]), [120, 0])
        self.assertEqual(list(ax.patches[0].xy[14]), [110, 0])
        self.assertEqual(list(ax.patches[0].xy[15]), [110, 0])
        self.assertEqual(list(ax.patches[0].xy[16]), [100, 0])
        self.assertEqual(len(ax.patches[0].xy), 17)
    
        # B polygon
        self.assertEqual(list(ax.patches[1].xy[ 0]), [100, 3])
        self.assertEqual(list(ax.patches[1].xy[ 1]), [100, 8])
        self.assertEqual(list(ax.patches[1].xy[ 2]), [110, 8])
        self.assertEqual(list(ax.patches[1].xy[ 3]), [110, 7])
        self.assertEqual(list(ax.patches[1].xy[ 4]), [120, 7])
        self.assertEqual(list(ax.patches[1].xy[ 5]), [120, 7])
        self.assertEqual(list(ax.patches[1].xy[ 6]), [130, 7])
        self.assertEqual(list(ax.patches[1].xy[ 7]), [130, 14])
        self.assertEqual(list(ax.patches[1].xy[ 8]), [140, 14])
        self.assertEqual(list(ax.patches[1].xy[ 9]), [140, 11])
        self.assertEqual(list(ax.patches[1].xy[10]), [130, 11])
        self.assertEqual(list(ax.patches[1].xy[11]), [130, 4])
        self.assertEqual(list(ax.patches[1].xy[12]), [120, 4])
        self.assertEqual(list(ax.patches[1].xy[13]), [120, 3])
        self.assertEqual(list(ax.patches[1].xy[14]), [110, 3])
        self.assertEqual(list(ax.patches[1].xy[15]), [110, 3])
        self.assertEqual(list(ax.patches[1].xy[16]), [100, 3])
        self.assertEqual(len(ax.patches[1].xy), 17)
    
        # C polygon
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 0]), [100,    8])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 1]), [100, 14.3])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 2]), [110, 14.3])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 3]), [110, 10.3])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 4]), [120, 10.3])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 5]), [120, 10.4])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 6]), [130, 10.4])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 7]), [130, 21.1])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 8]), [140, 21.1])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 9]), [140,    14])
        self.assertListAlmostEqual(list(ax.patches[2].xy[10]), [130,    14])
        self.assertListAlmostEqual(list(ax.patches[2].xy[11]), [130,    7])
        self.assertListAlmostEqual(list(ax.patches[2].xy[12]), [120,    7])
        self.assertListAlmostEqual(list(ax.patches[2].xy[13]), [120,    7])
        self.assertListAlmostEqual(list(ax.patches[2].xy[14]), [110,    7])
        self.assertListAlmostEqual(list(ax.patches[2].xy[15]), [110,    8])
        self.assertListAlmostEqual(list(ax.patches[2].xy[16]), [100,    8])
        self.assertEqual(len(ax.patches[2].xy), 17)
    
        # Error band
        self.assertEqual(ax.patches[3]._x0, 100)
        self.assertEqual(ax.patches[3]._width, 10)

        self.assertAlmostEqual(ax.patches[3]._height**2 / 4,
            0.2**2 + 0.4**2 + 0.1**2 + 0.1**2 + 0.4**2 + 0.1**2)
        self.assertAlmostEqual(2 * ax.patches[3]._y0 + ax.patches[3]._height, 14.3 * 2)

        self.assertEqual(ax.patches[4]._x0, 110)
        self.assertEqual(ax.patches[4]._width, 10)
        self.assertAlmostEqual(ax.patches[4]._height**2 / 4,
                               0.3**2 + 0.5**2 + 0.1**2)
        self.assertAlmostEqual(2 * ax.patches[4]._y0 + ax.patches[4]._height, 10.3 * 2)

        self.assertEqual(ax.patches[5]._x0, 120)
        self.assertEqual(ax.patches[5]._width, 10)
        self.assertAlmostEqual(ax.patches[5]._height**2 / 4,
                               0.4**2 + 0.4**2 + 0.2**2)
        self.assertAlmostEqual(2 * ax.patches[5]._y0 + ax.patches[5]._height, 10.4 * 2)

        self.assertEqual(ax.patches[6]._x0, 130)
        self.assertEqual(ax.patches[6]._width, 10)
        self.assertAlmostEqual(ax.patches[6]._height**2 / 4,
            0.5**2 + 0.5**2 + 0.2**2 + 0.6**2 + 0.5**2 + 0.3**2)
        self.assertAlmostEqual(2 * ax.patches[6]._y0 + ax.patches[6]._height, 21.1 * 2)

        # X points
        self.assertEqual(list(ax.lines[0].get_xdata()), [105, 115, 125, 135])
        self.assertEqual(list(ax.lines[0].get_ydata()), [13, 8, 9, 20])

        # X error
        sqrt2 = math.sqrt(2)
        sqrt13 = math.sqrt(13)
        vertical = ax.containers[1][2][1].get_segments()
        self.assertEqual(list(vertical[0][0]), [105, 13 - 0.1 * sqrt2])
        self.assertEqual(list(vertical[0][1]), [105, 13 + 0.1 * sqrt2])
        self.assertEqual(list(vertical[1][0]), [115, 7.9])
        self.assertEqual(list(vertical[1][1]), [115, 8.1])
        self.assertEqual(list(vertical[2][0]), [125, 8.8])
        self.assertEqual(list(vertical[2][1]), [125, 9.2])
        self.assertEqual(list(vertical[3][0]), [135, 20 - 0.1 * sqrt13])
        self.assertEqual(list(vertical[3][1]), [135, 20 + 0.1 * sqrt13])
        self.assertEqual(len(vertical), 4)

        horizontal = ax.containers[1][2][0].get_segments()
        self.assertEqual(list(horizontal[0][0]), [100, 13])
        self.assertEqual(list(horizontal[0][1]), [110, 13])
        self.assertEqual(list(horizontal[1][0]), [110, 8])
        self.assertEqual(list(horizontal[1][1]), [120, 8])
        self.assertEqual(list(horizontal[2][0]), [120, 9])
        self.assertEqual(list(horizontal[2][1]), [130, 9])
        self.assertEqual(list(horizontal[3][0]), [130, 20])
        self.assertEqual(list(horizontal[3][1]), [140, 20])
        self.assertEqual(len(horizontal), 4)

    def test_stat_outside_density(self):
        """Check that uncertainty when outside bins are merged"""
        hist = uhepp.UHeppHist("m", [100, 110, 120, 130, 140])
        hist.yields = {
            "a": uhepp.Yield([  1,   2,   3,   4,   5,   6],
                             [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]),
            "b": uhepp.Yield([  2,   3,   4,   3,   2,   1],
                             [0.4, 0.4, 0.5, 0.4, 0.5, 0.5]),
            "c": uhepp.Yield([3.1, 3.2, 3.3, 3.4, 3.5, 3.6],
                             [0.1, 0.1, 0.1, 0.2, 0.2, 0.3]),
            "x": uhepp.Yield([  6,   7,   8,   9,  10,  10],
                             [0.1, 0.1, 0.1, 0.2, 0.2, 0.3])
        }

        hist.stacks.append(uhepp.Stack([
                uhepp.StackItem(["a"], label="A"),
                uhepp.StackItem(["b"], label="B"),
                uhepp.StackItem(["c"], label="C"),
        ]))
        hist.stacks.append(uhepp.Stack([
                uhepp.StackItem(["x"], label="Data"),
        ], bartype="points"))

        hist.include_overflow = True
        hist.include_underflow = True
        hist.density_width = 10

        fig, ax = hist.render()
    
        # A polygon
        self.assertEqual(list(ax.patches[0].xy[ 0]), [100, 0])
        self.assertEqual(list(ax.patches[0].xy[ 1]), [100, 3])
        self.assertEqual(list(ax.patches[0].xy[ 2]), [110, 3])
        self.assertEqual(list(ax.patches[0].xy[ 3]), [110, 3])
        self.assertEqual(list(ax.patches[0].xy[ 4]), [120, 3])
        self.assertEqual(list(ax.patches[0].xy[ 5]), [120, 4])
        self.assertEqual(list(ax.patches[0].xy[ 6]), [130, 4])
        self.assertEqual(list(ax.patches[0].xy[ 7]), [130, 11])
        self.assertEqual(list(ax.patches[0].xy[ 8]), [140, 11])
        self.assertEqual(list(ax.patches[0].xy[ 9]), [140, 0])
        self.assertEqual(list(ax.patches[0].xy[10]), [130, 0])
        self.assertEqual(list(ax.patches[0].xy[11]), [130, 0])
        self.assertEqual(list(ax.patches[0].xy[12]), [120, 0])
        self.assertEqual(list(ax.patches[0].xy[13]), [120, 0])
        self.assertEqual(list(ax.patches[0].xy[14]), [110, 0])
        self.assertEqual(list(ax.patches[0].xy[15]), [110, 0])
        self.assertEqual(list(ax.patches[0].xy[16]), [100, 0])
        self.assertEqual(len(ax.patches[0].xy), 17)
    
        # B polygon
        self.assertEqual(list(ax.patches[1].xy[ 0]), [100, 3])
        self.assertEqual(list(ax.patches[1].xy[ 1]), [100, 8])
        self.assertEqual(list(ax.patches[1].xy[ 2]), [110, 8])
        self.assertEqual(list(ax.patches[1].xy[ 3]), [110, 7])
        self.assertEqual(list(ax.patches[1].xy[ 4]), [120, 7])
        self.assertEqual(list(ax.patches[1].xy[ 5]), [120, 7])
        self.assertEqual(list(ax.patches[1].xy[ 6]), [130, 7])
        self.assertEqual(list(ax.patches[1].xy[ 7]), [130, 14])
        self.assertEqual(list(ax.patches[1].xy[ 8]), [140, 14])
        self.assertEqual(list(ax.patches[1].xy[ 9]), [140, 11])
        self.assertEqual(list(ax.patches[1].xy[10]), [130, 11])
        self.assertEqual(list(ax.patches[1].xy[11]), [130, 4])
        self.assertEqual(list(ax.patches[1].xy[12]), [120, 4])
        self.assertEqual(list(ax.patches[1].xy[13]), [120, 3])
        self.assertEqual(list(ax.patches[1].xy[14]), [110, 3])
        self.assertEqual(list(ax.patches[1].xy[15]), [110, 3])
        self.assertEqual(list(ax.patches[1].xy[16]), [100, 3])
        self.assertEqual(len(ax.patches[1].xy), 17)
    
        # C polygon
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 0]), [100,    8])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 1]), [100, 14.3])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 2]), [110, 14.3])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 3]), [110, 10.3])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 4]), [120, 10.3])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 5]), [120, 10.4])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 6]), [130, 10.4])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 7]), [130, 21.1])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 8]), [140, 21.1])
        self.assertListAlmostEqual(list(ax.patches[2].xy[ 9]), [140,    14])
        self.assertListAlmostEqual(list(ax.patches[2].xy[10]), [130,    14])
        self.assertListAlmostEqual(list(ax.patches[2].xy[11]), [130,    7])
        self.assertListAlmostEqual(list(ax.patches[2].xy[12]), [120,    7])
        self.assertListAlmostEqual(list(ax.patches[2].xy[13]), [120,    7])
        self.assertListAlmostEqual(list(ax.patches[2].xy[14]), [110,    7])
        self.assertListAlmostEqual(list(ax.patches[2].xy[15]), [110,    8])
        self.assertListAlmostEqual(list(ax.patches[2].xy[16]), [100,    8])
        self.assertEqual(len(ax.patches[2].xy), 17)
    
        # Error band
        self.assertEqual(ax.patches[3]._x0, 100)
        self.assertEqual(ax.patches[3]._width, 10)

        self.assertAlmostEqual(ax.patches[3]._height**2 / 4,
            0.2**2 + 0.4**2 + 0.1**2 + 0.1**2 + 0.4**2 + 0.1**2)
        self.assertAlmostEqual(2 * ax.patches[3]._y0 + ax.patches[3]._height, 14.3 * 2)

        self.assertEqual(ax.patches[4]._x0, 110)
        self.assertEqual(ax.patches[4]._width, 10)
        self.assertAlmostEqual(ax.patches[4]._height**2 / 4,
                               0.3**2 + 0.5**2 + 0.1**2)
        self.assertAlmostEqual(2 * ax.patches[4]._y0 + ax.patches[4]._height, 10.3 * 2)

        self.assertEqual(ax.patches[5]._x0, 120)
        self.assertEqual(ax.patches[5]._width, 10)
        self.assertAlmostEqual(ax.patches[5]._height**2 / 4,
                               0.4**2 + 0.4**2 + 0.2**2)
        self.assertAlmostEqual(2 * ax.patches[5]._y0 + ax.patches[5]._height, 10.4 * 2)

        self.assertEqual(ax.patches[6]._x0, 130)
        self.assertEqual(ax.patches[6]._width, 10)
        self.assertAlmostEqual(ax.patches[6]._height**2 / 4,
            0.5**2 + 0.5**2 + 0.2**2 + 0.6**2 + 0.5**2 + 0.3**2)
        self.assertAlmostEqual(2 * ax.patches[6]._y0 + ax.patches[6]._height, 21.1 * 2)

        # X points
        self.assertEqual(list(ax.lines[0].get_xdata()), [105, 115, 125, 135])
        self.assertEqual(list(ax.lines[0].get_ydata()), [13, 8, 9, 20])

        # X error
        sqrt2 = math.sqrt(2)
        sqrt13 = math.sqrt(13)
        vertical = ax.containers[1][2][1].get_segments()
        self.assertEqual(list(vertical[0][0]), [105, 13 - 0.1 * sqrt2])
        self.assertEqual(list(vertical[0][1]), [105, 13 + 0.1 * sqrt2])
        self.assertEqual(list(vertical[1][0]), [115, 7.9])
        self.assertEqual(list(vertical[1][1]), [115, 8.1])
        self.assertEqual(list(vertical[2][0]), [125, 8.8])
        self.assertEqual(list(vertical[2][1]), [125, 9.2])
        self.assertEqual(list(vertical[3][0]), [135, 20 - 0.1 * sqrt13])
        self.assertEqual(list(vertical[3][1]), [135, 20 + 0.1 * sqrt13])
        self.assertEqual(len(vertical), 4)

        horizontal = ax.containers[1][2][0].get_segments()
        self.assertEqual(list(horizontal[0][0]), [100, 13])
        self.assertEqual(list(horizontal[0][1]), [110, 13])
        self.assertEqual(list(horizontal[1][0]), [110, 8])
        self.assertEqual(list(horizontal[1][1]), [120, 8])
        self.assertEqual(list(horizontal[2][0]), [120, 9])
        self.assertEqual(list(horizontal[2][1]), [130, 9])
        self.assertEqual(list(horizontal[3][0]), [130, 20])
        self.assertEqual(list(horizontal[3][1]), [140, 20])
        self.assertEqual(len(horizontal), 4)

