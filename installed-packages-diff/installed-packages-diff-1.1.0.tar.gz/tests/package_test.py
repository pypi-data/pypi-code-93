import unittest
from installed_packages_diff.package import Package
from installed_packages_diff.differ import create_diff


class PackageTest(unittest.TestCase):
  def test_valid_rpm_name(self):
    p = Package.parse("a-v1-1.9", type="rpm")
    self.assertEqual(p.name, "a")
    self.assertEqual(p.version, "v1-1.9")

  def test_valid_dpkg_name_with_dot_in_version(self):
    p = Package.parse("adduser\t3.115", type="dpkg")
    self.assertEqual("adduser", p.name)
    self.assertEqual("3.115", p.version)

  def test_valid_dpkg_name_without_opt_pkg_type(self):
    p = Package.parse("pkg\tversion+1234-foo_mips+yoyodyne", type="dpkg")
    self.assertEqual("pkg", p.name)
    self.assertEqual("version+1234-foo_mips+yoyodyne", p.version)

  def test_qual(self):
    p = Package.parse("a-v1-1", type="rpm")
    p2 = Package.parse("a-v1-1", type="rpm")
    self.assertEqual(p, p2)

  def test_missing_version(self):
    with self.assertRaises(ValueError):
      Package.parse("a")

  def test_valid_rpm_name2(self):
    p = Package.parse("libstdc++47-devel-32bit-4.7.2_20130108-0.19.3",
                      type="rpm")
    self.assertEqual(p.name, "libstdc++47-devel-32bit")
    self.assertEqual(p.version, "4.7.2_20130108-0.19.3")
