
import unittest
import numpy as np
from uhepp import Line, VLine, HLine

class LineTestCase(unittest.TestCase):
    """Test the implementation of Line"""

    def test_init_store(self):
        """Check that arguments to init are stored as members"""
        line = Line(125, [0, 200], linestyle=':', linewidth=3, color='r',
                    edgecolor='b')

        self.assertEqual(line.pos, 125)
        self.assertEqual(line.stretch, [0, 200])
        self.assertEqual(line.linewidth, 3)
        self.assertEqual(line.color, '#ff0000')
        self.assertEqual(line.edgecolor, '#0000ff')

    def test_init_default(self):
        """Check the default values for bartype and error"""
        line = Line(125)

        self.assertEqual(line.pos, 125)
        self.assertIsNone(line.stretch)
        self.assertEqual(line.style, {})

    def test_member_change(self):
        """Check that member variables can be changed"""
        line = Line(125)
        line.pos = 200
        line.stretch = (0, 100)
        line.color = 'blue'

        self.assertEqual(line.pos, 200)
        self.assertEqual(line.stretch, (0, 100))
        self.assertEqual(line.color, '#0000ff')

class VLineTestCase(unittest.TestCase):
    """Test the implementation of VLine"""

    def test_init(self):
        """Check that arguments to init are stored as members"""
        line = VLine(125)
        self.assertEqual(line.pos_x, 125)

class HLineTestCase(unittest.TestCase):
    """Test the implementation of HLine"""

    def test_init(self):
        """Check that arguments to init are stored as members"""
        line = HLine(125)
        self.assertEqual(line.pos_y, 125)
