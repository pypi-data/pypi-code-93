
import unittest
import numpy as np
from uhepp import _SmartDict

class SmartDictTestCase(unittest.TestCase):
    """Test the implementation of _SmartDict"""

    def test_init(self):
        """Check that the init stores the dict"""
        sdict = _SmartDict({"hello": 42})
        self.assertEqual(sdict.data["hello"], 42)

    def test_in(self):
        """Check the in operator"""
        data = {
            "hello": {
                "world": 42,
                "this": "that",
            },
            "other": "x"
        }
        sdict = _SmartDict(data)

        self.assertIn("hello", sdict)
        self.assertIn("hello.world", sdict)
        self.assertIn("hello.this", sdict)
        self.assertIn("other", sdict)

        self.assertNotIn("world", sdict)
        self.assertNotIn("hello.other", sdict)
        self.assertNotIn("this.that", sdict)

    def test_get(self):
        """Check that get returns the default if not found"""
        data = {
            "hello": {
                "world": 42,
                "this": "that",
            },
            "other": "x"
        }
        sdict = _SmartDict(data)

        self.assertEqual(sdict.get("hello", "def"),
                        {"world": 42, "this": "that"})
        self.assertEqual(sdict.get("hello.world", "def"), 42)
        self.assertEqual(sdict.get("hello.this", "def"), "that")
        self.assertEqual(sdict.get("other", "def"), "x")

        self.assertEqual(sdict.get("world", "def"), "def")
        self.assertEqual(sdict.get("hello.other", "def"), "def")
        self.assertEqual(sdict.get("this.that", "def"), "def")

    def test_getitem(self):
        """Check that get returns the default if not found"""
        data = {
            "hello": {
                "world": 42,
                "this": "that",
            },
            "other": "x"
        }
        sdict = _SmartDict(data)

        self.assertEqual(sdict["hello"],
                         {"world": 42, "this": "that"})
        self.assertEqual(sdict["hello.world"], 42)
        self.assertEqual(sdict["hello.this"], "that")
        self.assertEqual(sdict["other"], "x")

        self.assertRaises(KeyError, lambda: sdict["world"])
        self.assertRaises(KeyError, lambda: sdict["hello.other"])
        self.assertRaises(KeyError, lambda: sdict["this.that"])
