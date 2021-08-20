import unittest
from typing import Tuple, List

import feyn

from feyn._program import Program


class TestProgram(unittest.TestCase):
    def setUp(self):
        self.program = Program([0]*32)

    def test_len(self):
        with self.subTest("A single terminal has length 1"):
            self.program._codes[0]=10000
            self.assertEqual(len(self.program), 1)


        with self.subTest("A single unary has length 2"):
            self.program._codes[0]=1000
            self.assertEqual(len(self.program), 2)

        with self.subTest("A single arity 2 has length 3"):
            self.program._codes[0]=2000
            self.assertEqual(len(self.program), 3)

        with self.subTest("A more complex program"):
            self.program._codes[0:6] = [2001,2001,1001,10000,10001,10002] # + + log x0 x1 x2
            self.assertEqual(len(self.program), 6)
