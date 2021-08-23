import re


class Package(object):
  PKG_NAME_REGEX = {
    "rpm": re.compile("^\s*(.+)-([^\-\s]+-[^\-\s]+)\s*$"),
    "dpkg": re.compile("^\s*(.+)\t([^\s]+)\s*$")
  }

  @classmethod
  def parse(cls, pkg_name: str, type="rpm"):
    result = Package.PKG_NAME_REGEX[type].fullmatch(pkg_name)
    if not result:
      raise ValueError(f"Invalid package name '{pkg_name}'.")

    return Package(result.group(1), result.group(2))

  def __init__(self, name, version):
    self.name = name
    self.version = version

  def __repr__(self):
    return f"Package(name={self.name},version={self.version})"

  def __hash__(self):
    return hash((self.name, self.version))

  def __eq__(self, other):
    return (self.name, self.version) == (other.name, other.version)
