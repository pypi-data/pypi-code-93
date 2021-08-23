import io
import unittest
from installed_packages_diff.config import load_config


class ConfigTest(unittest.TestCase):
  def test_full(self):
    config_yaml = """groups:
  db:
    servers:
      - username: root
        hostname: dbdev
        excludes:
          - "missing"
      - username: root
        hostname: dblive
  web:
    servers:
      - username: root
        hostname: webdev
        excludes:
          - "missing"
      - username: root
        hostname: weblive
"""
    config = load_config(io.StringIO(config_yaml))
    self.assertEqual([g.name for g in config.groups], ["db", "web"])
    self.assertEqual(
        [(s.hostname, s.username) for s in config.groups[1].servers],
        [("webdev", "root"), ("weblive", "root")])
    self.assertEqual(config.groups[1].servers[0].excludes, {"missing"})
    self.assertEqual(config.groups[1].servers[1].excludes, set())
