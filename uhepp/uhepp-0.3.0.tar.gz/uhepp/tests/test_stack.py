
import unittest
import numpy as np
from uhepp import Stack

class StackTestCase(unittest.TestCase):
    """Test the implementation of Stack"""

    def test_init_store(self):
        """Check that arguments to init are stored as members"""
        stack= Stack(["si-ggh", "si-vbf"], 'step', 'syst')

        self.assertEqual(stack.content, ['si-ggh', 'si-vbf'])
        self.assertEqual(stack.bartype, 'step')
        self.assertEqual(stack.error, 'syst')

    def test_init_default(self):
        """Check the default values for bartype and error"""
        stack= Stack(["si-ggh", "si-vbf"])

        self.assertEqual(stack.content, ['si-ggh', 'si-vbf'])
        self.assertEqual(stack.bartype, 'stepfilled')
        self.assertEqual(stack.error, 'stat')

    def test_init_copy(self):
        """Check that arguments to init are copied"""
        stackitems = ['si-ggh', 'si-vbf']
        stack = Stack(stackitems, 'step', 'syst')

        stackitems.append('si-other')

        self.assertEqual(stack.content, ['si-ggh', 'si-vbf'])
        self.assertEqual(stack.bartype, 'step')
        self.assertEqual(stack.error, 'syst')


    def test_member_change(self):
        """Check that member variables can be changed"""
        stack = Stack(["si-ggh", "si-vbf"], 'step', 'syst')

        stack.content.append('si-tth')
        stack.bartype = 'points'
        stack.error = 'env'

        self.assertEqual(stack.content, ['si-ggh', 'si-vbf', 'si-tth'])
        self.assertEqual(stack.bartype, 'points')
        self.assertEqual(stack.error, "env")

    def test_illegal_bartype(self):
        """Check that an illegal bartype raises an exception"""
        self.assertRaises(ValueError, Stack, ["si-ggh", "si-vbf"],
                          'bubble', 'syst')

        stack = Stack(["si-ggh", "si-vbf"], 'step', 'syst')
        def assign():
            stack.bartype = 'bubble'
        self.assertRaises(ValueError, assign)

    def test_illegal_error(self):
        """Check that an illegal error raises an exception"""
        self.assertRaises(ValueError, Stack, ["si-ggh", "si-vbf"],
                          'step', 'var')

        stack = Stack(["si-ggh", "si-vbf"], 'step', 'syst')
        def assign2():
            stack.error = 'var'
        self.assertRaises(ValueError, assign2)

