# This file is placed in the Public Domain.

import unittest

from obj import Object, dump, json

class Test_JSON(unittest.TestCase):
    def test_jsondump(self):
        o = Object()
        o.test = "bla"
        self.assertEqual(json(o), "{'test': 'bla'}")
