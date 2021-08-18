
import unittest
import uhepp
import uhepp.utils as uu

class AddEnvelopTestCase(unittest.TestCase):
    """Test the implementation of add_envelope"""

    def setUp(self):
        """Create toy histogram"""
        self.hist = uhepp.UHeppHist("m", [0, 100, 200])

        y_bkg = uhepp.Yield([0, 1000, 500, 100],
                            var_up={"es": [0, 900, 500, 200]},
                            var_down={"es": [0, 1100, 550, 50]})
        y_sig = uhepp.Yield([0, 10, 30, 10],
                            var_up={"es": [0, 5, 35, 10]},
                            var_down={"es": [0, 10, 35, 5]})
        y_data = uhepp.Yield([0, 950, 550, 100], [0, 31, 23, 10])

        self.hist.yields = {"bkg": y_bkg, "sig": y_sig, "data": y_data}
        self.hist.stacks = [
            uhepp.Stack([
                uhepp.StackItem(["bkg"], label="Background"),
                uhepp.StackItem(["sig"], label="Background"),
            ]),
            uhepp.Stack([
                uhepp.StackItem(["data"], label="Data"),
            ], bartype="points"),
        ]
        self.hist.ratio = [
            uhepp.RatioItem(["data"], ["bkg", "sig"], bartype="points")
        ]

    def test_copy(self):
        """Check that the returned histogram is a copy"""
        env = uu.add_envelope(self.hist, "es")
        self.assertEqual(len(self.hist.stacks), 2)

        self.hist.stacks.pop()
        self.hist.stacks.pop()

        self.assertEqual(len(env.stacks), 4)

    def test_up_main(self):
        """Check the added stack item for up variation"""
        env = uu.add_envelope(self.hist, "es")

        self.assertEqual(env.stacks[2].bartype, "step")
        self.assertEqual(len(env.stacks[2].content), 1)
        self.assertEqual(env.stacks[2].content[0].yield_names,
                         ["bkg/es/up", "sig/es/up"])
        self.assertEqual(env.stacks[2].content[0].label, "Up")
        self.assertEqual(env.stacks[2].content[0].color, "#ff0000")


    def test_down_main(self):
        """Check the added stack item for down variation"""
        env = uu.add_envelope(self.hist, "es")

        self.assertEqual(env.stacks[3].bartype, "step")
        self.assertEqual(len(env.stacks[3].content), 1)
        self.assertEqual(env.stacks[3].content[0].yield_names,
                         ["bkg/es/down", "sig/es/down"])
        self.assertEqual(env.stacks[3].content[0].label, "Down")
        self.assertEqual(env.stacks[3].content[0].color, "#0000ff")

    def test_up_ratio(self):
        """Check the added ratio item for up variation"""
        env = uu.add_envelope(self.hist, "es")

        self.assertEqual(env.ratio[1].bartype, "step")
        self.assertEqual(env.ratio[1].numerator, 
                         ["bkg/es/up", "sig/es/up"])
        self.assertEqual(env.ratio[1].denominator, ["bkg", "sig"])
        self.assertEqual(env.ratio[1].color, "#ff0000")

    def test_down_ratio(self):
        """Check the added ratio item for down variation"""
        env = uu.add_envelope(self.hist, "es")

        self.assertEqual(env.ratio[2].bartype, "step")
        self.assertEqual(env.ratio[2].numerator, 
                         ["bkg/es/down", "sig/es/down"])
        self.assertEqual(env.ratio[2].denominator, ["bkg", "sig"])
        self.assertEqual(env.ratio[2].color, "#0000ff")

    def test_main_stack_index(self):
        """Check that the stack can be selected"""
        env = uu.add_envelope(self.hist, "es", stack_index=1)

        self.assertEqual(env.stacks[2].bartype, "step")
        self.assertEqual(len(env.stacks[2].content), 1)
        self.assertEqual(env.stacks[2].content[0].yield_names,
                         ["data/es/up"])

class MergeTestCase(unittest.TestCase):
    """Test the implementation of merge"""

    def setUp(self):
        """Create toy histogram"""
        self.hist_a = uhepp.UHeppHist("m", [0, 100, 200])

        y_bkg = uhepp.Yield([0, 1000, 500, 100])
        y_sig = uhepp.Yield([0, 10, 30, 10])
        y_data = uhepp.Yield([0, 950, 550, 100], [0, 31, 23, 10])

        self.hist_a.yields = {"bkg": y_bkg, "sig": y_sig, "data": y_data}
        self.hist_a.stacks = [
            uhepp.Stack([
                uhepp.StackItem(["bkg"], label="Background"),
                uhepp.StackItem(["sig"], label="Background"),
            ]),
            uhepp.Stack([
                uhepp.StackItem(["data"], label="Data"),
            ], bartype="points"),
        ]
        self.hist_a.ratio = [
            uhepp.RatioItem(["data"], ["bkg", "sig"], bartype="points")
        ]

        self.hist_b = uhepp.UHeppHist("m", [0, 100, 200])

        y_bkg = uhepp.Yield([0, 100, 50, 10])
        y_sig = uhepp.Yield([0, 1, 3, 1])
        y_data = uhepp.Yield([0, 95, 55, 10], [0, 10, 7, 3])

        self.hist_b.yields = {"bkg": y_bkg, "sig": y_sig, "data": y_data}
        self.hist_b.stacks = [
            uhepp.Stack([
                uhepp.StackItem(["bkg"], label="Background"),
                uhepp.StackItem(["sig"], label="Background"),
            ]),
            uhepp.Stack([
                uhepp.StackItem(["data"], label="Data"),
            ], bartype="points"),
        ]
        self.hist_b.ratio = [
            uhepp.RatioItem(["data"], ["bkg", "sig"], bartype="points")
        ]

    def test_merge_rename(self):
        """Check that the new yields are renamed to avoid name clash"""
        merged = uu.merge(self.hist_a, self.hist_b)

        self.assertIn("h0_bkg", merged.yields)
        self.assertIn("h0_sig", merged.yields)
        self.assertIn("h0_data", merged.yields)
        self.assertIn("h1_bkg", merged.yields)
        self.assertIn("h1_sig", merged.yields)
        self.assertIn("h1_data", merged.yields)

    def test_merge_reference(self):
        """Check that the renamed yield names are referenced"""
        merged = uu.merge(self.hist_a, self.hist_b)

        self.assertEqual(merged.stacks[0].content[0].yield_names,
                         ["h0_bkg"])
        self.assertEqual(merged.stacks[-1].content[0].yield_names,
                         ["h1_data"])

        self.assertEqual(merged.ratio[0].numerator, ["h0_data"])
        self.assertEqual(merged.ratio[-1].denominator, ["h1_bkg", "h1_sig"])

    def test_merge_complete(self):
        """Check that all the merge is complete"""
        merged = uu.merge(self.hist_a, self.hist_b)

        self.assertEqual(len(merged.stacks), 4)
        self.assertEqual(len(merged.ratio), 2)

    def test_different_binning(self):
        """Check that merge() with different bin edges raises an exception"""
        hist_b = uhepp.UHeppHist("m", [0, 100, 200, 300])

        self.assertRaises(ValueError, uu.merge, self.hist_a, hist_b)

    def test_copy(self):
        """Check that the returned histogram is a copy"""
        merged = uu.merge(self.hist_a, self.hist_b)
        self.assertEqual(len(self.hist_a.stacks), 2)

        self.hist_a.stacks.pop()
        self.hist_b.stacks.pop()

        self.assertEqual(len(merged.stacks), 4)
