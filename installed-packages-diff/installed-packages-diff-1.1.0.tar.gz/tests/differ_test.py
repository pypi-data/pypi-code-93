import unittest

from installed_packages_diff.differ import create_diff
from installed_packages_diff.package import Package


class DifferTest(unittest.TestCase):
  def test_diff_of_equal_versions_is_empty(self):
    a = Package("a", "v1-1.0")
    a2 = Package("a", "v1-1.0")

    diff = create_diff([a], [a2], includeEqual=True)

    self.assertEqual([("a", 'v1-1.0', 'v1-1.0')], diff)

  def test_diff_of_nonequal_versions(self):
    a = Package("a", "v1-1.0")
    a2 = Package("a", "v1-2.0")

    diff = create_diff([a], [a2], includeEqual=True)

    self.assertEqual([("a", 'v1-1.0', 'v1-2.0')], diff)

  def test_diff_of_equal_duplicate_versions(self):
    a = Package("a", "v1-1.0")
    a2 = Package("a", "v1-1.0")
    a3 = Package("a", "v1-2.0")
    a4 = Package("a", "v1-2.0")

    diff = create_diff([a, a3], [a2, a4], includeEqual=True)

    self.assertEqual([("a", 'v1-1.0', 'v1-1.0'),
                      ("a", 'v1-2.0', 'v1-2.0')], diff)

  def test_diff_of_nonequal_duplicate_versions(self):
    a = Package("a", "v1-1.0")
    a2 = Package("a", "v1-2.0")
    a3 = Package("a", "v1-3.0")
    a4 = Package("a", "v1-4.0")

    diff = create_diff([a, a2], [a3, a4], includeEqual=True)

    self.assertEqual([("a", 'v1-1.0', 'missing'),
                      ("a", 'v1-2.0', 'missing'),
                      ("a", 'missing', 'v1-3.0'),
                      ("a", 'missing', 'v1-4.0'),
                      ], diff)

  def test_all(self):
    a = Package("a", "v1-1.0")
    b = Package("b", "v1-1.0")
    c1 = Package("c", "v1-1.0")
    c2 = Package("c", "v1-1.1")
    d1 = Package("d", "v1-1.0")
    d2 = Package("d", "v2-1.0")

    diff = create_diff([a, c1, d1], [b, c2, d2], includeEqual=True)

    self.assertEqual([("a", "v1-1.0", "missing"),
                      ("c", "v1-1.0", "v1-1.1"),
                      ("d", "v1-1.0", "v2-1.0"),
                      ("b", "missing", "v1-1.0")],
                     diff)

  def test_exclude_source(self):
    a = Package("a", "v1-1.0")
    b = Package("b", "v1-1.0")
    c1 = Package("c", "v1-1.0")
    c2 = Package("c", "v1-1.1")
    d1 = Package("d", "v1-1.0")
    d2 = Package("d", "v2-1.0")

    diff = create_diff([a, c1, d1], [b, c2, d2], aExcludes=["missing"], includeEqual=True)

    self.assertEqual([("a", "v1-1.0", "missing"),
                      ("c", "v1-1.0", "v1-1.1"),
                      ("d", "v1-1.0", "v2-1.0")],
                     diff)

  def test_exclude_target(self):
    a = Package("a", "v1-1.0")
    b = Package("b", "v1-1.0")
    c1 = Package("c", "v1-1.0")
    c2 = Package("c", "v1-1.1")
    d1 = Package("d", "v1-1.0")
    d2 = Package("d", "v2-1.0")

    diff = create_diff([a, c1, d1], [b, c2, d2], bExcludes=["missing"], includeEqual=True)

    self.assertEqual([("c", "v1-1.0", "v1-1.1"),
                      ("d", "v1-1.0", "v2-1.0"),
                      ("b", "missing", "v1-1.0")],
                     diff)

  def test_exclude_equal(self):
    a = Package("a", "v1-1.0")
    b = Package("b", "v1-1.0")
    c1 = Package("c", "v1-1.1")
    c2 = Package("c", "v1-1.1")
    d1 = Package("d", "v1-1.0")
    d2 = Package("d", "v2-1.0")

    diff = create_diff([a, c1, d1], [b, c2, d2], includeEqual=False)

    self.assertEqual([("a", "v1-1.0", "missing"),
                      ("d", "v1-1.0", "v2-1.0"),
                      ("b", "missing", "v1-1.0")],
                     diff)
