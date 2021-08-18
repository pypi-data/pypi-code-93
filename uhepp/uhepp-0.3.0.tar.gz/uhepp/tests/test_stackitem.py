
import unittest
import numpy as np
from uhepp import StackItem

class StackItemTestCase(unittest.TestCase):
    """Test the implementation of StackItem"""

    def test_init_store(self):
        """Check that arguments to init are stored as members"""
        stackitem = StackItem(["ggh", "vbf"], label="Signal", color='k')

        self.assertEqual(stackitem.yield_names, ['ggh', 'vbf'])
        self.assertEqual(stackitem.label, 'Signal')
        self.assertEqual(stackitem.color, '#000000')

    def test_init_copy(self):
        """Check that arguments to init are copied"""
        yields = ['ggh', 'vbf']
        stackitem = StackItem(yields, label="Signal", color="k")

        yields.append('43')

        self.assertEqual(stackitem.yield_names, ['ggh', 'vbf'])
        self.assertEqual(stackitem.label, 'Signal')
        self.assertEqual(stackitem.color, '#000000')

    def test_member_change(self):
        """Check that member variables can be changed"""
        stackitem = StackItem(["ggh", "vbf"], label="Signal", color='#000000')

        stackitem.yield_names.append('tth')
        stackitem.color = 'r'

        self.assertEqual(stackitem.yield_names, ['ggh', 'vbf', 'tth'])
        self.assertEqual(stackitem.label, 'Signal')
        self.assertEqual(stackitem.color, "#ff0000")

    def test_illegal_style(self):
        """Check that an illegal style key raises an exception"""
        self.assertRaises(ValueError, StackItem, ['ggh'],
                          label="Signal", whaterever=32)

    def test_color_rgb(self):
        """Check that a 3-tuple is converted to a hex string"""
        self.assertEqual(StackItem._parse_color((0.1, 0.9, 0)), "#1ae600")

    def test_color_rgba(self):
        """Check that a 4-tuple is converted to a hex string"""
        self.assertEqual(StackItem._parse_color((0.1, 0.9, 0, 0.1)),
                         "#1ae6001a")

    def test_line_style_legal(self):
        """Check that legal line styles are accepted"""
        StackItem(["ggh", "vbf"], "Signal", linestyle='--')
        StackItem(["ggh", "vbf"], "Signal", linestyle='-.')
        StackItem(["ggh", "vbf"], "Signal", linestyle=':')
        StackItem(["ggh", "vbf"], "Signal", linestyle='-')

    def test_line_style_illegal(self):
        """Check that invalid line styles raise an exception"""
        self.assertRaises(ValueError, StackItem, ["ggh", "vbf"], "Signal",
                          linestyle='+')

    def test_line_width(self):
        """Check that line widths are converted to floats"""
        stackitem = StackItem(["ggh", "vbf"], "Signal", linewidth='3')

        self.assertEqual(stackitem.linewidth, 3)
        self.assertIsInstance(stackitem.linewidth, float)

    def test_default_style(self):
        """Check that the default styles are None"""
        stackitem = StackItem(["ggh", "vbf"], "Signal")

        self.assertIsNone(stackitem.linestyle)
        self.assertIsNone(stackitem.linewidth)
        self.assertIsNone(stackitem.color)
        self.assertIsNone(stackitem.edgecolor)

    def test_style(self):
        """Check that style contains all styles"""
        stackitem = StackItem(["ggh", "vbf"], "Signal", linestyle=':',
                              color='r', linewidth=3, edgecolor='b')

        self.assertEqual(stackitem.style,
                         {'color': '#ff0000', 'edgecolor': '#0000ff',
                          'linewidth': 3, 'linestyle': ':'})

    def test_style_copy(self):
        """Check that style is a copy of the internal dict"""
        stackitem = StackItem(["ggh", "vbf"], "Signal", linestyle=':',
                              color='r', linewidth=3, edgecolor='b')

        style = stackitem.style
        style["color"] = 'xxx'

        self.assertEqual(stackitem.style["color"], "#ff0000")
