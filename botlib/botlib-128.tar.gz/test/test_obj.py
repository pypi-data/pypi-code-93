# This file is placed in the Public Domain.

import ob
import os
import unittest

from ob import Db, O, Object, gettype, getwd

k = ob.krn.kernel()
wd = getwd()

class Test_Object(unittest.TestCase):

    def test_O(self):
        o = O()
        self.assertEqual(type(o), O)

    def test_Object(self):
        o = Object()
        self.assertEqual(type(o), Object)

    def test_intern1(self):
        o = Object()
        self.assertTrue(o.__stp__)

    def test_intern2(self):
        o = Object()
        self.assertFalse(o)

    def test_json(self):
        o = Object()
        self.assertTrue("<ob.Object" in Object.__dorepr__(o))

    def test_intern4(self):
        o = Object()
        self.assertTrue(gettype(o) in o.__stp__)

    def test_empty(self):
        o = Object()
        self.assertTrue(not o)

    def test_final(self):
        o = Object()
        o.test = "bla"
        o.last()
        self.assertEqual(o.test, "bla")

    def test_stamp(self):
        o = Object()
        o.save()
        self.assertTrue(o.__stp__)

    def test_uuid(self):
        o = Object()
        p = o.save()
        uuid1 = p.split(os.sep)[1]
        p = o.save()
        uuid2 = p.split(os.sep)[1]
        self.assertEqual(uuid1, uuid2)

    def test_attribute(self):
        o = Object()
        o.bla = "test"
        p = o.save()
        oo = Object()
        oo.load(p)
        self.assertEqual(oo.bla, "test")

    def test_changeattr(self):
        o = Object()
        o.bla = "test"
        p = o.save()
        oo = Object()
        oo.load(p)
        oo.bla = "mekker"
        pp = oo.save()
        ooo = Object()
        ooo.load(pp)
        self.assertEqual(ooo.bla, "mekker")

    def test_last(self):
        o = Object()
        o.bla = "test"
        o.save()
        oo = Object()
        oo.last()
        self.assertEqual(oo.bla, "test")

    def test_last2(self):
        o = Object()
        o.save()
        uuid1 = o.__stp__.split(os.sep)[1]
        o.last()
        uuid2 = o.__stp__.split(os.sep)[1]
        self.assertEqual(uuid1, uuid2)

    def test_last3(self):
        o = Object()
        o.last()
        s = o.__stp__
        uuid1 = o.__stp__.split(os.sep)[1]
        o.save()
        uuid2 = o.__stp__.split(os.sep)[1]
        self.assertEqual(uuid1, uuid2)

    def test_lastest(self):
        o = Object()
        o.bla = "test"
        o.save()
        oo = Object()
        p = oo.last()
        oo.bla = "mekker"
        oo.save()
        ooo = Object()
        p = ooo.last()
        self.assertEqual(ooo.bla, "mekker")

    def test_merge(self):
        o = Object()
        o.a = 1
        o.b = "1"
        o.c = ["1"]
        o.d = {"a": 1}
        oo = Object()
        oo.a = 1
        oo.b = "1"
        oo.c = ["1"]
        oo.d = {"a": 1}
        oo.merge(o)
        self.assertEqual(o.c, ["1"])

    def test_nested(self):
        o = Object()
        o.o = Object()
        o.o.o = Object()
        o.o.o.test = "bla"
        p = o.save()
        oo = Object()
        oo.load(p)
        self.assertEqual(o.o.o.test, "bla")
