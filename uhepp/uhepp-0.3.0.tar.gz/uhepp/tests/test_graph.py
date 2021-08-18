
import unittest
import numpy as np
from uhepp import Graph

class GraphTetCase(unittest.TestCase):
    """Test the implementation of Graph"""

    def test_init_store(self):
        """Check that arguments to init are stored as members"""
        graph = Graph([1, 2, 3], [1, 4, 9], color='b', graphtype="line")

        self.assertEqual(graph.x_values, [1, 2, 3])
        self.assertEqual(graph.y_values, [1, 4, 9])
        self.assertEqual(graph.color, "#0000ff")
        self.assertEqual(graph.graphtype, "line")

    def test_init_default(self):
        """Check the default values for bartype and error"""
        graph = Graph([1, 2, 3], [1, 4, 9])

        self.assertEqual(graph.x_values, [1, 2, 3])
        self.assertEqual(graph.y_values, [1, 4, 9])
        self.assertEqual(graph.style, {})
        self.assertEqual(graph.graphtype, "points")

    def test_member_change(self):
        """Check that member variables can be changed"""
        graph = Graph([1, 2, 3], [1, 4, 9])
        graph.x_values = [2, 3, 4]
        graph.y_values = [4, 9, 16]
        graph.color = "red"
        graph.graphtype = "line"

        self.assertEqual(graph.x_values, [2, 3, 4])
        self.assertEqual(graph.y_values, [4, 9, 16])
        self.assertEqual(graph.color, "#ff0000")
        self.assertEqual(graph.graphtype, "line")
