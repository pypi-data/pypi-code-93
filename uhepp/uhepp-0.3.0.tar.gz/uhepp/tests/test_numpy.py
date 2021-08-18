
import unittest
import numpy as np
from uhepp import UHeppHist, Yield, Graph

class NumpyTestCase(unittest.TestCase):
    """Test that assigned values are converted to plain python"""

    def test_edges(self):
        """Check assigning a numpy array to edges converts it to python"""
        edges = np.linspace(0, 100, 11)
        hist = UHeppHist("m", edges)

        self.assertIsInstance(hist.bin_edges, list) 
        self.assertIsInstance(hist.bin_edges[0], (int, float)) 
        self.assertNotIsInstance(hist.bin_edges[0], (np.float64, np.int64))

    def test_base(self):
        """Check assigning a numpy array to base yields converts it to python"""
        base = np.arange(10)**2
        yield_ = Yield(base)

        self.assertIsInstance(yield_.base, list)
        self.assertIsInstance(yield_.base[0], (int, float)) 
        self.assertNotIsInstance(yield_.base[0], (np.float64, np.int64))

    def test_stat(self):
        """Check assigning a numpy array to stat yields converts it to python"""
        base = np.arange(10)**2
        stat = np.ones(10) * 8
        yield_ = Yield(base, stat)

        self.assertIsInstance(yield_.stat, list)
        self.assertIsInstance(yield_.stat[0], (int, float)) 
        self.assertNotIsInstance(yield_.stat[0], (np.float64, np.int64))

    def test_syst(self):
        """Check assigning a numpy array to syst yields converts it to python"""
        base = np.arange(10)**2
        syst = np.ones(10) * 8
        yield_ = Yield(base, syst=syst)

        self.assertIsInstance(yield_.syst, list)
        self.assertIsInstance(yield_.syst[0], (int, float)) 
        self.assertNotIsInstance(yield_.syst[0], (np.float64, np.int64))

    def test_var_up(self):
        """Check assigning a numpy array to var yields converts it to python"""
        base = np.arange(10)**2
        var = base + np.ones(10) * 8
        yield_ = Yield(base)
        yield_.add_var("DETECTOR", var_up=var, var_down=var)

        self.assertIsInstance(yield_.var_up("DETECTOR"), list)
        self.assertIsInstance(yield_.var_up("DETECTOR")[0], (int, float)) 
        self.assertNotIsInstance(yield_.var_up("DETECTOR")[0],
                                 (np.float64, np.int64))

    def test_var_down(self):
        """Check assigning a numpy array to var yields converts it to python"""
        base = np.arange(10)**2
        var = base + np.ones(10) * 8
        yield_ = Yield(base)
        yield_.add_var("DETECTOR", var_up=var, var_down=var)

        self.assertIsInstance(yield_.var_down("DETECTOR"), list)
        self.assertIsInstance(yield_.var_down("DETECTOR")[0], (int, float)) 
        self.assertNotIsInstance(yield_.var_down("DETECTOR")[0],
                                 (np.float64, np.int64))


    def test_graph_x(self):
        """Check assigning a numpy array to graph converts it to python"""
        series = np.arange(5) / 5
        graph = Graph(series, series)

        self.assertIsInstance(graph.x_values, list)
        self.assertIsInstance(graph.x_values[0], (int, float)) 
        self.assertNotIsInstance(graph.x_values[0], (np.float64, np.int64))

    def test_graph_y(self):
        """Check assigning a numpy array to graph converts it to python"""
        series = np.arange(5) / 5
        graph = Graph(series, series)

        self.assertIsInstance(graph.y_values, list)
        self.assertIsInstance(graph.y_values[0], (int, float)) 
        self.assertNotIsInstance(graph.y_values[0], (np.float64, np.int64))

    def test_graph_xerr(self):
        """Check assigning a numpy array to graph converts it to python"""
        series = np.arange(5) / 5
        graph = Graph(series, series)
        graph.x_errors = series
        graph.y_errors = series

        self.assertIsInstance(graph.x_errors, list)
        self.assertIsInstance(graph.x_errors[0], (int, float)) 
        self.assertNotIsInstance(graph.x_errors[0], (np.float64, np.int64))

    def test_graph_yerr(self):
        """Check assigning a numpy array to graph converts it to python"""
        series = np.arange(5) / 5
        graph = Graph(series, series)
        graph.x_errors = series
        graph.y_errors = series

        self.assertIsInstance(graph.y_errors, list)
        self.assertIsInstance(graph.y_errors[0], (int, float)) 
        self.assertNotIsInstance(graph.y_errors[0], (np.float64, np.int64))
