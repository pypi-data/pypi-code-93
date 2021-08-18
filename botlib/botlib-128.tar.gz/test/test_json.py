# This file is placed in the Public Domain.

import ob
import json
import unittest


class Test_JSON(unittest.TestCase):
    def test_jsonO(self):
        o = ob.O()
        o.test = "bla"
        v = json.dumps(o, default=o.__default__)
        self.assertTrue(repr(o) == v)

    def test_jsonObject(self):
        o = ob.Object()
        o.test = "bla"
        v = json.dumps(o, default=o.__default__)
        self.assertEqual(repr(o), v)

    def test_jsonreconstructO(self):
        o = ob.O()
        o.test = "bla"
        v = json.dumps(o, default=o.__default__)
        vv = json.loads(v, object_hook=ob.Object)
        self.assertEqual(repr(o), repr(vv))

    def test_jsonreconstructObject(self):
        o = ob.Object()
        o.test = "bla"
        v = json.dumps(o, default=o.__default__)
        vv = json.loads(v, object_hook=ob.Object)
        self.assertEqual(repr(o), repr(vv))
