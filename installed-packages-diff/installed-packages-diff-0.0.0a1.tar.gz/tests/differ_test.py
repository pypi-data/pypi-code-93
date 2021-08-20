import unittest
from installed_packages_diff.package import Package
from installed_packages_diff.differ import create_diff


class DifferTest(unittest.TestCase):
  def test_all(self):
    a = Package("a", "v1-1.0")
    b = Package("b", "v1-1.0")
    c1 = Package("c", "v1-1.0")
    c2 = Package("c", "v1-1.1")
    d1 = Package("d", "v1-1.0")
    d2 = Package("d", "v2-1.0")

    diff = create_diff([a, c1, d1], [b, c2, d2])

    self.assertEqual({'a': ['v1-1.0', 'missing'],
                      'b': ['missing', 'v1-1.0'],
                      'c': ['v1-1.0', 'v1-1.1'],
                      'd': ['v1-1.0', 'v2-1.0']},
                     diff)

  def test_exclude_source(self):
    a = Package("a", "v1-1.0")
    b = Package("b", "v1-1.0")
    c1 = Package("c", "v1-1.0")
    c2 = Package("c", "v1-1.1")
    d1 = Package("d", "v1-1.0")
    d2 = Package("d", "v2-1.0")

    diff = create_diff([a, c1, d1], [b, c2, d2], aExcludes=["missing"])

    self.assertEqual({'a': ['v1-1.0', 'missing'],
                      'c': ['v1-1.0', 'v1-1.1'],
                      'd': ['v1-1.0', 'v2-1.0']},
                     diff)

  def test_exclude_target(self):
    a = Package("a", "v1-1.0")
    b = Package("b", "v1-1.0")
    c1 = Package("c", "v1-1.0")
    c2 = Package("c", "v1-1.1")
    d1 = Package("d", "v1-1.0")
    d2 = Package("d", "v2-1.0")

    diff = create_diff([a, c1, d1], [b, c2, d2], bExcludes=["missing"])

    self.assertEqual({'b': ['missing', 'v1-1.0'],
                      'c': ['v1-1.0', 'v1-1.1'],
                      'd': ['v1-1.0', 'v2-1.0']},
                     diff)

  def test_include_equal(self):
    a = Package("a", "v1-1.0")
    b = Package("b", "v1-1.0")
    c1 = Package("c", "v1-1.0")
    c2 = Package("c", "v1-1.1")
    d1 = Package("d", "v1-1.0")
    d2 = Package("d", "v2-1.0")
    e = Package("e", "v3-1.0")

    diff = create_diff([a, c1, d1, e], [b, c2, d2, e], includeEqual=True)

    self.assertEqual({'a': ['v1-1.0', 'missing'],
                      'b': ['missing', 'v1-1.0'],
                      'c': ['v1-1.0', 'v1-1.1'],
                      'd': ['v1-1.0', 'v2-1.0'],
                      "e": ["v3-1.0", "v3-1.0"]},
                     diff)
