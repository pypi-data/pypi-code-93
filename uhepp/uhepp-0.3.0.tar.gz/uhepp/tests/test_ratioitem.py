
import unittest
import numpy as np
from uhepp import RatioItem

class RatioItemTestCase(unittest.TestCase):
    """Test the implementation of RatioItem"""

    def test_init_store(self):
        """Check that arguments to init are stored as members"""
        stack = RatioItem(["ggh"], ["vbf"], 'step', 'syst',
                          linestyle=':', linewidth=3, color='r',
                          edgecolor='b')

        self.assertEqual(stack.numerator, ['ggh'])
        self.assertEqual(stack.denominator, ['vbf'])
        self.assertEqual(stack.bartype, 'step')
        self.assertEqual(stack.error, 'syst')
        self.assertEqual(stack.color, '#ff0000')

    def test_init_default(self):
        """Check the default values for bartype and error"""
        stack = RatioItem(["ggh"])

        self.assertEqual(stack.numerator, ['ggh'])
        self.assertEqual(stack.denominator, [])
        self.assertEqual(stack.bartype, 'step')
        self.assertEqual(stack.error, 'stat')
        self.assertEqual(stack.den_error, 'stat')

    def test_init_copy(self):
        """Check that arguments to init are copied"""
        stackitems = ['ggh']
        stack = RatioItem(stackitems, stackitems)

        stackitems.append('other')
        self.assertEqual(stack.numerator, ['ggh'])
        self.assertEqual(stack.denominator, ['ggh'])

    def test_member_change(self):
        """Check that member variables can be changed"""
        stack = RatioItem(["ggh"], ["vbf"])

        stack.numerator.append('tth')
        stack.denominator.append('other')
        stack.bartype = 'points'
        stack.error = 'env'
        stack.den_error = 'syst'
        stack.linewidth = 3

        self.assertEqual(stack.numerator, ['ggh', 'tth'])
        self.assertEqual(stack.denominator, ['vbf', 'other'])
        self.assertEqual(stack.bartype, 'points')
        self.assertEqual(stack.error, "env")
        self.assertEqual(stack.den_error, "syst")
        self.assertEqual(stack.linewidth, 3)
