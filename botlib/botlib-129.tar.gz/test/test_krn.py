# This file is placed in the Public Domain.

import unittest

from obj import getmain
from obj.run import Cfg

k = getmain("k")

class Test_Kernel(unittest.TestCase):

    def test_cfg(self):
        self.assertEqual(type(k.cfg), Cfg)
