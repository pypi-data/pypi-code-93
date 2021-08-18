
import os
import unittest
from uhepp import from_yaml, from_yamls, from_json, from_jsons
import uhepp

class FromTestCase(unittest.TestCase):
    """Base class to test from_XXX methods"""
    @staticmethod
    def rel_path(filename):
        """Convert a filename to a file-relative path"""
        return os.path.join(os.path.dirname(__file__), filename)

    def assertTrivialHist(self, hist, **kwds):
        """Assert the argument is the trivial toy histogram"""
        self.assertEqual(hist.version, "0.1")
        self.assertEqual(hist.date, "2020-11-10T23:39:00+01:00")
        self.assertEqual(hist.filename, "hello")
        self.assertEqual(hist.symbol, "x")
        self.assertEqual(hist.bin_edges, list(range(6)))
        self.assertEqual(hist.stacks, [])
        self.assertEqual(hist.ratio, [])
        self.assertEqual(hist.yields, {})

        self.assertIsNone(hist.author)
        self.assertIsNone(hist.lumi)
        self.assertIsNone(hist.ratio_max)

    def assertBasicHist(self, hist, **kwds):
        """Assert the argument is the basic toy histogram"""
        self.assertEqual(hist.version, "0.1")
        self.assertEqual(hist.date, "2020-11-10T23:39:00+01:00")
        self.assertEqual(hist.filename, "hello")
        self.assertEqual(hist.author, "Frank Sauerburger")
        self.assertEqual(hist.symbol, "x")
        self.assertEqual(hist.bin_edges, list(range(6)))

        stack, = hist.stacks
        self.assertEqual(stack.bartype, "points")
        content, = stack.content
        self.assertEqual(content.yield_names, ["data"])
        self.assertEqual(content.label, "Data")

        data_yield = hist.yields["data"]
        self.assertEqual(data_yield.base, [1.1, 1.9, 2.8, 4.2, 5, 6, 7])

        self.assertEqual(len(hist.yields), 1)

class FromYamlTestCase(FromTestCase):
    """Check that importing from yaml works"""

    def test_trivial_hist_string(self):
        """Check that the trivial hist is restores from a string"""
        with open(self.rel_path("trivial_hist.yaml")) as yaml_file:
            yaml_string = yaml_file.read()

        hist = from_yamls(yaml_string)
        self.assertTrivialHist(hist)

    def test_trivial_hist(self):
        """Check that importing a trivial hist restores all values"""
        hist = from_yaml(self.rel_path("trivial_hist.yaml"))
        self.assertTrivialHist(hist)

    def test_trivial_hist_render(self):
        """Check that rendering a trivial hist succeeds"""
        hist = from_yaml(self.rel_path("trivial_hist.yaml"))
        self.assertIsNotNone(hist.render())

    def test_basic_hist(self):
        """Check that importing a basic hist restores all values"""
        hist = from_yaml(self.rel_path("basic_hist.yaml"))

    def test_basic_hist_render(self):
        """Check that rendering a basic hist succeeds"""
        hist = from_yaml(self.rel_path("basic_hist.yaml"))
        self.assertIsNotNone(hist.render())

class FromJsonTestCase(FromTestCase):
    """Check that importing from json works"""

    def test_trivial_hist_string(self):
        """Check that the trivial hist is restores from a string"""
        with open(self.rel_path("trivial_hist.json")) as json_file:
            json_string = json_file.read()

        hist = from_jsons(json_string)
        self.assertTrivialHist(hist)

    def test_trivial_hist(self):
        """Check that importing a trivial hist restores all values"""
        hist = from_json(self.rel_path("trivial_hist.json"))
        self.assertTrivialHist(hist)

    def test_trivial_hist_render(self):
        """Check that rendering a trivial hist succeeds"""
        hist = from_json(self.rel_path("trivial_hist.json"))
        self.assertIsNotNone(hist.render())

    def test_basic_hist(self):
        """Check that importing a basic hist restores all values"""
        hist = from_json(self.rel_path("basic_hist.json"))

    def test_basic_hist_render(self):
        """Check that rendering a basic hist succeeds"""
        hist = from_json(self.rel_path("basic_hist.json"))
        self.assertIsNotNone(hist.render())

class CloneTestCase(unittest.TestCase):
    """Test the implementation of clone() using to_json and from_json"""

    def test_indepenent(self):
        """Check that cloning produces an independent object"""
        hist = uhepp.UHeppHist("m", [0, 100, 200, 300])
        hist.ratio = [uhepp.RatioItem([], [])]

        new_hist = hist.clone()
        hist.ratio = []
        self.assertEqual(len(new_hist.ratio), 1)
