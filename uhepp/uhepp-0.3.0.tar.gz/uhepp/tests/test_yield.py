
import unittest
import numpy as np
from uhepp import Yield

class YieldTestCase(unittest.TestCase):
    """Test the implementation of Yield"""

    def test_zeros(self):
        """Check that zeros returns zeros of base-length"""
        data = Yield([1, 2, 3, 4])
        self.assertEqual(len(data._zeros()), 4)

    def test_sanitize_present(self):
        """Check that a array is returned if a list is given"""
        data = Yield([1, 2, 3, 4])
        array = data._sanitize([1, 2, 3, 4])
        self.assertEqual(list(array), [1, 2, 3, 4])
        self.assertIsInstance(array, np.ndarray)

    def test_sanitize_missing(self):
        """Check that a None is returned if None is given"""
        data = Yield([1, 2, 3])
        missing = data._sanitize(None)
        self.assertIsNone(missing)

    def test_sanitize_length(self):
        """Check sanitize raises a ValueEror on bin count mismatch"""
        data = Yield([1, 2, 3])
        self.assertRaises(ValueError, data._sanitize, [1, 2, 3, 4])

    def test_linear(self):
        """Check that the arrays are added linearly"""
        array_a = np.array([1, 2, 3])
        array_b = np.array([4, 5, 2])

        result = Yield._linear(array_a, array_b, lambda a, b: a + b)
        self.assertEqual(list(result), [5, 7, 5])

    def test_linear_None(self):
        """Check that the None arrays are ignored"""
        array_a = np.array([1, 2, 3])

        result = Yield._linear(array_a, None, lambda a, b: a + b)
        self.assertEqual(list(result), [1, 2, 3])

        result = Yield._linear(None, array_a, lambda a, b: a + b)
        self.assertEqual(list(result), [1, 2, 3])

        result = Yield._linear(None, None, lambda a, b: a + b)
        self.assertIsNone(result)

    def test_quadratic(self):
        """Check that the arrays are added quadratic"""
        array_a = np.array([1, 2, 3])
        array_b = np.array([4, 5, 2])

        result = Yield._quadratic(array_a, array_b, lambda a, b: a + b)
        self.assertListAlmostEqual([x**2 for x in result],
                                   [17, 29, 13])

    def test_quadratic_None(self):
        """Check that the None arrays are ignored"""
        array_a = np.array([1, 2, 3])

        result = Yield._quadratic(array_a, None, lambda a, b: a + b)
        self.assertListAlmostEqual(list(result), [1, 2, 3])

        result = Yield._quadratic(None, array_a, lambda a, b: a + b)
        self.assertListAlmostEqual(list(result), [1, 2, 3])

        result = Yield._quadratic(None, None, lambda a, b: a + b)
        self.assertIsNone(result)

    def test_optional_args(self):
        """Check that all arguments except base are optional"""
        data = Yield([1, 2, 3, 4])

        self.assertEqual(list(data._base), [1, 2, 3, 4])
        self.assertIsInstance(data._base, np.ndarray)

    def test_all_args_store(self):
        """Check that the values for all arguments are stored internally"""
        data = Yield([1, 2, 3, 4],
                     [0.1, 0.2, 0.3, 0.4],
                     [1, 1, 1, 1],
                     var_up={'exp': [1, 2, 2, 1]},
                     var_down={'theo': [2, 1, 1, 2]})

        self.assertEqual(list(data._base), [1, 2, 3, 4])
        self.assertEqual(list(data._stat), [0.1, 0.2, 0.3, 0.4])
        self.assertEqual(list(data._syst), [1, 1, 1, 1])
        self.assertIsInstance(data._base, np.ndarray)
        self.assertIsInstance(data._stat, np.ndarray)
        self.assertIsInstance(data._syst, np.ndarray)

        self.assertEqual(list(data._var_up.keys()), ['exp'])
        self.assertEqual(list(data._var_down.keys()), ['theo'])

        self.assertEqual(list(data._var_up['exp']), [1, 2, 2, 1])
        self.assertEqual(list(data._var_down['theo']), [2, 1, 1, 2])
        self.assertIsInstance(data._var_up['exp'], np.ndarray)
        self.assertIsInstance(data._var_down['theo'], np.ndarray)

    def test_base(self):
        """Check that base returns the base yield"""
        data = Yield([1, 2, 3, 4])

        self.assertEqual(data.base, [1, 2, 3, 4])
        self.assertIsInstance(data.base, list)

    def test_base_copy(self):
        """Check that base returns a copy of the base yield"""
        data = Yield([1, 2, 3, 4])

        self.assertEqual(data.base, [1, 2, 3, 4])
        base = data.base    
        base.append(5)
        self.assertEqual(data.base, [1, 2, 3, 4])

    def test_stat(self):
        """Check that stat returns the stat uncertainty"""
        data = Yield([1, 2, 3, 4],
                     [0.1, 0.2, 0.3, 0.4])

        self.assertEqual(data.stat, [0.1, 0.2, 0.3, 0.4])
        self.assertIsInstance(data.stat, list)

    def test_stat_fill(self):
        """Check that stat returns the 0 if stat is missing"""
        data = Yield([1, 2, 3, 4])

        self.assertEqual(data.stat, [0.0, 0.0, 0.0, 0.0])
        self.assertIsInstance(data.stat, list)

    def test_stat_copy(self):
        """Check that stat returns a copy of the stat uncertainty"""
        data = Yield([1, 2, 3, 4],
                     [0.1, 0.2, 0.3, 0.4])

        self.assertEqual(data.stat, [0.1, 0.2, 0.3, 0.4])
        stat = data.stat    
        stat.append(5)
        self.assertEqual(data.stat, [0.1, 0.2, 0.3, 0.4])

    def test_syst(self):
        """Check that syst returns the syst uncertainty"""
        data = Yield([1, 2, 3, 4],
                     syst=[0.1, 0.2, 0.3, 0.4])

        self.assertEqual(data.syst, [0.1, 0.2, 0.3, 0.4])
        self.assertIsInstance(data.syst, list)

    def test_syst_fill(self):
        """Check that syst returns the 0 if syst is missing"""
        data = Yield([1, 2, 3, 4])

        self.assertEqual(data.syst, [0.0, 0.0, 0.0, 0.0])
        self.assertIsInstance(data.syst, list)

    def test_syst_copy(self):
        """Check that syst returns a copy of the syst uncertainty"""
        data = Yield([1, 2, 3, 4],
                     syst=[0.1, 0.2, 0.3, 0.4])

        self.assertEqual(data.syst, [0.1, 0.2, 0.3, 0.4])
        syst = data.syst    
        syst.append(5)
        self.assertEqual(data.syst, [0.1, 0.2, 0.3, 0.4])

    def test_var_names(self):
        """Check that variation_names returns a list of all variations"""
        data = Yield([1, 2, 3, 4],
                     var_up={"tes": [2, 2, 2, 2], "theory": [2, 4, 6, 8]},
                     var_down={"jes": [2, 2, 4, 4], "theory": [2, 4, 6, 8]})

        self.assertEqual(set(data.variations),
                         set(["tes", "jes", "theory"]))
        self.assertIsInstance(data.variations, list)

        # No up
        data = Yield([1, 2, 3, 4],
                     var_down={"jes": [2, 2, 4, 4], "theory": [2, 4, 6, 8]})

        self.assertEqual(set(data.variations),
                         set(["jes", "theory"]))

        # No down
        data = Yield([1, 2, 3, 4],
                     var_up={"jes": [2, 2, 4, 4], "theory": [2, 4, 6, 8]})

        self.assertEqual(set(data.variations),
                         set(["jes", "theory"]))

    def test_var_names__no_var(self):
        """Check that variation_names returns an empty list"""
        data = Yield([1, 2, 3, 4])

        self.assertEqual(data.variations, [])

    def test_variation(self):
        """Check that variation_up/down returns the yield if found in dicts"""
        data = Yield([1, 2, 3, 4],
                     var_up={"tes": [2, 2, 2, 2], "theory": [2, 4, 6, 8]},
                     var_down={"jes": [2, 2, 1, 1], "theory": [-2, -4, -6, -8]})

        self.assertEqual(data.var_up("theory"), [2, 4, 6, 8])
        self.assertEqual(data.var_down("theory"), [-2, -4, -6, -8])

    def test_variation__onsided_this(self):
        """Test variation_up/down with one-sided var found in dict"""
        data = Yield([1, 2, 3, 4],
                     var_up={"tes": [2, 2, 2, 2], "theory": [2, 4, 6, 8]},
                     var_down={"jes": [2, 2, 1, 1], "theory": [-2, -4, -6, -8]})

        self.assertEqual(data.var_up("tes"), [2, 2, 2, 2])
        self.assertEqual(data.var_down("jes"), [2, 2, 1, 1])

        self.assertIsInstance(data.var_up("tes"), list)
        self.assertIsInstance(data.var_down("jes"), list)

    def test_variation__onsided_other(self):
        """Test variation_up/down with one-sided var found in other dict"""
        data = Yield([1, 2, 3, 4],
                     var_up={"tes": [2, 2, 2, 2], "theory": [2, 4, 6, 8]},
                     var_down={"jes": [2, 2, 1, 1], "theory": [-2, -4, -6, -8]})

        self.assertEqual(data.var_up("jes"), [0, 2, 5, 7]) 
        self.assertEqual(data.var_down("tes"), [0, 2, 4, 6])

        self.assertIsInstance(data.var_up("jes"), list)
        self.assertIsInstance(data.var_down("tes"), list)

    def test_variation_unknown(self):
        """Test variation_up/down with unknown variation"""
        data = Yield([1, 2, 3, 4],
                     var_up={"tes": [2, 2, 2, 2], "theory": [2, 4, 6, 8]},
                     var_down={"jes": [2, 2, 1, 1], "theory": [-2, -4, -6, -8]})

        self.assertEqual(data.var_up("ckkw"), [1, 2, 3, 4])
        self.assertEqual(data.var_down("ckkw"), [1, 2, 3, 4])

        self.assertIsInstance(data.var_up("ckkw"), list)
        self.assertIsInstance(data.var_down("ckkw"), list)

    def test_iter_var(self):
        """Check that iter_vars returns all names and variations"""
        data = Yield([1, 2, 3, 4],
                     var_up={"tes": [2, 2, 2, 2], "theory": [2, 4, 6, 8]},
                     var_down={"jes": [2, 2, 1, 1], "theory": [-2, -4, -6, -8]})

        items = sorted(data.iter_vars())
        self.assertEqual(items[0], ("jes", [0, 2, 5, 7], [2, 2, 1, 1]))
        self.assertEqual(items[1], ("tes", [2, 2, 2, 2],  [0, 2, 4, 6]))
        self.assertEqual(items[2], ("theory",
                                    [2, 4, 6, 8],
                                    [-2, -4, -6, -8]))
        self.assertEqual(len(items), 3)

    def test_add_var_new(self):
        """Check add_var adds a new up/down variation"""
        data = Yield([1, 2, 3, 4])

        data.add_var("tes", var_up=[2, 3, 4, 5])
        self.assertEqual(data.variations, ["tes"])
        self.assertEqual(data.var_up("tes"), [2, 3, 4, 5])

        data.add_var("jes", var_down=[2, 3, 4, 5])
        self.assertEqual(sorted(data.variations), ["jes", "tes"])
        self.assertEqual(data.var_down("jes"), [2, 3, 4, 5])

        data.add_var("theory", var_up=[1, 1, 1, 1], var_down=[3, 3, 3, 3])
        self.assertEqual(sorted(data.variations),
                          ["jes", "tes", "theory"])
        self.assertEqual(data.var_up("theory"), [1, 1, 1, 1])
        self.assertEqual(data.var_down("theory"), [3, 3, 3, 3])

    def test_add_var_overwrite(self):
        """Check add_var overwrites existing up/down variations"""
        data = Yield([1, 2, 3, 4],
                     var_up={"tes": [2, 2, 2, 2], "theory": [2, 4, 6, 8]},
                     var_down={"jes": [2, 2, 1, 1], "theory": [-2, -4, -6, -8]})

        data.add_var("tes", var_up=[2, 3, 4, 5])
        self.assertEqual(data.var_up("tes"), [2, 3, 4, 5])

        data.add_var("jes", var_down=[2, 3, 4, 5])
        self.assertEqual(data.var_down("jes"), [2, 3, 4, 5])

        data.add_var("theory", var_up=[1, 1, 1, 1], var_down=[3, 3, 3, 3])
        self.assertEqual(data.var_up("theory"), [1, 1, 1, 1])
        self.assertEqual(data.var_down("theory"), [3, 3, 3, 3])


    def assertListAlmostEqual(self, iter_a, iter_b, *args, **kwds):
        """Check that the contents of both lists are almost equal"""
        for item_a, item_b in zip(iter_a, iter_b):
            self.assertAlmostEqual(item_a, item_b, *args, **kwds)

        self.assertEqual(len(iter_a), len(iter_b))

    def test_add_number(self):
        """Check the result of adding a number to a yield"""
        data = Yield([1, 2, 3, 4], [0.1, 0.2, 0.3, 0.4], [0.2, 0.2, 0.4, 0.4],
                     var_up={"tes": [2, 2, 2, 2], "theory": [2, 4, 6, 8]},
                     var_down={"jes": [2, 2, 1, 1], "theory": [-2, -4, -6, -8]})

        data = data + 5
        self.assertEqual(data.base, [6, 7, 8, 9])
        self.assertEqual(data.stat, [0.1, 0.2, 0.3, 0.4])
        self.assertEqual(data.syst, [0.2, 0.2, 0.4, 0.4])

        self.assertEqual(data.var_up("tes"), [7, 7, 7, 7])
        self.assertEqual(data.var_down("tes"), [5, 7, 9, 11])

        self.assertEqual(data.var_up("jes"), [5, 7, 10, 12])
        self.assertEqual(data.var_down("jes"), [7, 7, 6, 6])

        self.assertEqual(data.var_up("theory"), [7, 9, 11, 13])
        self.assertEqual(data.var_down("theory"), [3, 1, -1, -3])

    def test_add_yield(self):
        """Check the result of adding two yields"""
        data_a = Yield([1, 2, 3, 4], [0.1, 0.2, 0.3, 0.4], [0.2, 0.2, 0.4, 0.4],
                       var_up={"tes": [2, 2, 2, 2],
                               "theory": [2, 4, 6, 8]},
                       var_down={"jes": [2, 2, 1, 1],
                                 "theory": [-2, -4, -6, -8]})

        data_b = Yield([0, 3, 2, 1], [0.1, 0.2, 0.2, 0.1], [0.2, 0.3, 0.3, 0.3],
                       var_up={"jer": [1, 2, 2, 1],
                               "theory": [2, 4, 6, 8]},
                       var_down={"jes": [1, 1, 1, 1],
                                 "theory": [-1, -2, -3, -4]})

        data = data_a + data_b
        self.assertEqual(data.base, [1, 5, 5, 5])
        self.assertListAlmostEqual([x**2 for x in data.stat], [0.02, 0.08, 0.13, 0.17])
        self.assertListAlmostEqual([x**2 for x in data.syst], [0.08, 0.13, 0.25, 0.25])

        self.assertEqual(data.var_up("tes"), [2, 5, 4, 3])
        self.assertEqual(data.var_down("tes"), [0, 5, 6, 7])

        self.assertEqual(data.var_up("jes"), [-1, 7, 8, 8])
        self.assertEqual(data.var_down("jes"), [3, 3, 2, 2])

        self.assertEqual(data.var_up("jer"), [2, 4, 5, 5])
        self.assertEqual(data.var_down("jer"), [0, 6, 5, 5])

        self.assertEqual(data.var_up("theory"), [4, 8, 12, 16])
        self.assertEqual(data.var_down("theory"), [-3, -6, -9, -12])

    def test_add_no_uncert_self(self):
        """Check adding yields without self uncertainty"""
        data_a = Yield([1, 2, 3, 4])

        data_b = Yield([0, 3, 2, 1], [0.1, 0.2, 0.2, 0.1], [0.2, 0.3, 0.3, 0.3],
                       var_up={"jer": [1, 2, 2, 1],
                               "theory": [2, 4, 6, 8]},
                       var_down={"jes": [1, 1, 1, 1],
                                 "theory": [-1, -2, -3, -4]})

        data = data_a + data_b
        self.assertEqual(data.base, [1, 5, 5, 5])
        self.assertListAlmostEqual(data.stat, [0.1, 0.2, 0.2, 0.1])
        self.assertListAlmostEqual(data.syst, [0.2, 0.3, 0.3, 0.3])

        self.assertEqual(data.var_up("jes"), [0, 7, 6, 5])
        self.assertEqual(data.var_down("jes"), [2, 3, 4, 5])

        self.assertEqual(data.var_up("jer"), [2, 4, 5, 5])
        self.assertEqual(data.var_down("jer"), [0, 6, 5, 5])

        self.assertEqual(data.var_up("theory"), [3, 6, 9, 12])
        self.assertEqual(data.var_down("theory"), [0, 0, 0, 0])

    def test_add_no_uncert_other(self):
        data_a = Yield([1, 2, 3, 4])

        data_b = Yield([0, 3, 2, 1], [0.1, 0.2, 0.2, 0.1], [0.2, 0.3, 0.3, 0.3],
                       var_up={"jer": [1, 2, 2, 1],
                               "theory": [2, 4, 6, 8]},
                       var_down={"jes": [1, 1, 1, 1],
                                 "theory": [-1, -2, -3, -4]})

        data = data_b + data_a
        self.assertEqual(data.base, [1, 5, 5, 5])
        self.assertListAlmostEqual(data.stat, [0.1, 0.2, 0.2, 0.1])
        self.assertListAlmostEqual(data.syst, [0.2, 0.3, 0.3, 0.3])

        self.assertEqual(data.var_up("jes"), [0, 7, 6, 5])
        self.assertEqual(data.var_down("jes"), [2, 3, 4, 5])

        self.assertEqual(data.var_up("jer"), [2, 4, 5, 5])
        self.assertEqual(data.var_down("jer"), [0, 6, 5, 5])

        self.assertEqual(data.var_up("theory"), [3, 6, 9, 12])
        self.assertEqual(data.var_down("theory"), [0, 0, 0, 0])

    def test_add_different_bin_count(self):
        """Check that a value error is raised if the bin count differs"""
        data_a = Yield([1, 2, 3, 4])
        data_b = Yield([0, 3, 2, 1, 5])

        self.assertRaises(ValueError, lambda: data_a + data_b)

    def test_copy_init_args(self):
        """Check that init argument arrays are copied"""
        array = np.array([1, 2, 3, 4])
        data = Yield(array, array, array,
                     var_up={"jer": array},
                     var_down={"jes": array})

        array[0] = -1
        self.assertEqual(data.base, [1, 2, 3, 4])
        self.assertEqual(data.stat, [1, 2, 3, 4])
        self.assertEqual(data.syst, [1, 2, 3, 4])
        self.assertEqual(data.var_up("jer"), [1, 2, 3, 4])
        self.assertEqual(data.var_down("jes"), [1, 2, 3, 4])

    def test_init_array_length(self):
        """Check that calling init with inconsistent bins raises an error"""
        self.assertRaises(ValueError, Yield, [1, 2, 3, 4], [1, 2, 3])
        self.assertRaises(ValueError, Yield, [1, 2, 3, 4], syst=[1, 2, 3])
        self.assertRaises(ValueError, Yield, [1, 2, 3, 4],
                          var_up={"tes": [1, 2, 3]})
        self.assertRaises(ValueError, Yield, [1, 2, 3, 4],
                          var_down={"tes": [1, 2, 3]})

    def test_var_add(self):
        """Check that adding a var with inconsistent bins raises an error"""
        data = Yield([1, 2, 3, 4])
        self.assertRaises(ValueError, data.add_var, "tes", var_up=[1, 2, 3])
        self.assertRaises(ValueError, data.add_var, "tes", var_down=[1, 2, 3])

    def test_radd_number(self):
        """Check the result of adding a number to a yield"""
        data = Yield([1, 2, 3, 4], [0.1, 0.2, 0.3, 0.4], [0.2, 0.2, 0.4, 0.4],
                     var_up={"tes": [2, 2, 2, 2], "theory": [2, 4, 6, 8]},
                     var_down={"jes": [2, 2, 1, 1], "theory": [-2, -4, -6, -8]})

        data = 5 + data
        self.assertEqual(data.base, [6, 7, 8, 9])
        self.assertEqual(data.stat, [0.1, 0.2, 0.3, 0.4])
        self.assertEqual(data.syst, [0.2, 0.2, 0.4, 0.4])

        self.assertEqual(data.var_up("tes"), [7, 7, 7, 7])
        self.assertEqual(data.var_down("tes"), [5, 7, 9, 11])

        self.assertEqual(data.var_up("jes"), [5, 7, 10, 12])
        self.assertEqual(data.var_down("jes"), [7, 7, 6, 6])

        self.assertEqual(data.var_up("theory"), [7, 9, 11, 13])
        self.assertEqual(data.var_down("theory"), [3, 1, -1, -3])

    ####### Subtract
    def test_sub_number(self):
        """Check the result of subtracting a number to a yield"""
        data = Yield([1, 2, 3, 4], [0.1, 0.2, 0.3, 0.4], [0.2, 0.2, 0.4, 0.4],
                     var_up={"tes": [2, 2, 2, 2], "theory": [2, 4, 6, 8]},
                     var_down={"jes": [2, 2, 1, 1], "theory": [-2, -4, -6, -8]})

        data = data - (-5)
        self.assertEqual(data.base, [6, 7, 8, 9])
        self.assertEqual(data.stat, [0.1, 0.2, 0.3, 0.4])
        self.assertEqual(data.syst, [0.2, 0.2, 0.4, 0.4])

        self.assertEqual(data.var_up("tes"), [7, 7, 7, 7])
        self.assertEqual(data.var_down("tes"), [5, 7, 9, 11])

        self.assertEqual(data.var_up("jes"), [5, 7, 10, 12])
        self.assertEqual(data.var_down("jes"), [7, 7, 6, 6])

        self.assertEqual(data.var_up("theory"), [7, 9, 11, 13])
        self.assertEqual(data.var_down("theory"), [3, 1, -1, -3])

    def test_sub_yield(self):
        """Check the result of subing two yields"""
        data_a = Yield([1, 2, 3, 4], [0.1, 0.2, 0.3, 0.4], [0.2, 0.2, 0.4, 0.4],
                       var_up={"tes": [2, 2, 2, 2],
                               "theory": [2, 4, 6, 8]},
                       var_down={"jes": [2, 2, 1, 1],
                                 "theory": [-2, -4, -6, -8]})

        data_b = Yield([-0, -3, -2, -1], [0.1, 0.2, 0.2, 0.1], [0.2, 0.3, 0.3, 0.3],
                       var_up={"jer": [-1, -2, -2, -1],
                               "theory": [-2, -4, -6, -8]},
                       var_down={"jes": [-1, -1, -1, -1],
                                 "theory": [1, 2, 3, 4]})

        data = data_a - data_b
        self.assertEqual(data.base, [1, 5, 5, 5])
        self.assertListAlmostEqual([x**2 for x in data.stat], [0.02, 0.08, 0.13, 0.17])
        self.assertListAlmostEqual([x**2 for x in data.syst], [0.08, 0.13, 0.25, 0.25])

        self.assertEqual(data.var_up("tes"), [2, 5, 4, 3])
        self.assertEqual(data.var_down("tes"), [0, 5, 6, 7])

        self.assertEqual(data.var_up("jes"), [-1, 7, 8, 8])
        self.assertEqual(data.var_down("jes"), [3, 3, 2, 2])

        self.assertEqual(data.var_up("jer"), [2, 4, 5, 5])
        self.assertEqual(data.var_down("jer"), [0, 6, 5, 5])

        self.assertEqual(data.var_up("theory"), [4, 8, 12, 16])
        self.assertEqual(data.var_down("theory"), [-3, -6, -9, -12])

    def test_sub_no_uncert_self(self):
        """Check subing yields without self uncertainty"""
        data_a = Yield([1, 2, 3, 4])

        data_b = Yield([-0, -3, -2, -1], [0.1, 0.2, 0.2, 0.1], [0.2, 0.3, 0.3, 0.3],
                       var_up={"jer": [-1, -2, -2, -1],
                               "theory": [-2, -4, -6, -8]},
                       var_down={"jes": [-1, -1, -1, -1],
                                 "theory": [1, 2, 3, 4]})

        data = data_a - data_b
        self.assertEqual(data.base, [1, 5, 5, 5])
        self.assertListAlmostEqual(data.stat, [0.1, 0.2, 0.2, 0.1])
        self.assertListAlmostEqual(data.syst, [0.2, 0.3, 0.3, 0.3])

        self.assertEqual(data.var_up("jes"), [0, 7, 6, 5])
        self.assertEqual(data.var_down("jes"), [2, 3, 4, 5])

        self.assertEqual(data.var_up("jer"), [2, 4, 5, 5])
        self.assertEqual(data.var_down("jer"), [0, 6, 5, 5])

        self.assertEqual(data.var_up("theory"), [3, 6, 9, 12])
        self.assertEqual(data.var_down("theory"), [0, 0, 0, 0])

    def test_sub_no_uncert_other(self):
        data_a = Yield([-1, -2, -3, -4])

        data_b = Yield([0, 3, 2, 1], [0.1, 0.2, 0.2, 0.1], [0.2, 0.3, 0.3, 0.3],
                       var_up={"jer": [1, 2, 2, 1],
                               "theory": [2, 4, 6, 8]},
                       var_down={"jes": [1, 1, 1, 1],
                                 "theory": [-1, -2, -3, -4]})

        data = data_b - data_a
        self.assertEqual(data.base, [1, 5, 5, 5])
        self.assertListAlmostEqual(data.stat, [0.1, 0.2, 0.2, 0.1])
        self.assertListAlmostEqual(data.syst, [0.2, 0.3, 0.3, 0.3])

        self.assertEqual(data.var_up("jes"), [0, 7, 6, 5])
        self.assertEqual(data.var_down("jes"), [2, 3, 4, 5])

        self.assertEqual(data.var_up("jer"), [2, 4, 5, 5])
        self.assertEqual(data.var_down("jer"), [0, 6, 5, 5])

        self.assertEqual(data.var_up("theory"), [3, 6, 9, 12])
        self.assertEqual(data.var_down("theory"), [0, 0, 0, 0])

    def test_sub_different_bin_count(self):
        """Check that a value error is raised if the bin count differs"""
        data_a = Yield([1, 2, 3, 4])
        data_b = Yield([0, 3, 2, 1, 5])

        self.assertRaises(ValueError, lambda: data_a - data_b)

    def test_rsub_number(self):
        """Check the result of subtracting a number to a yield"""
        data = Yield([1, 2, 3, 4], [0.1, 0.2, 0.3, 0.4], [0.2, 0.2, 0.4, 0.4],
                     var_up={"tes": [2, 2, 2, 2], "theory": [2, 4, 6, 8]},
                     var_down={"jes": [2, 2, 1, 1], "theory": [-2, -4, -6, -8]})

        data = -5 - data
        self.assertEqual(data.base, [-6, -7, -8, -9])
        self.assertEqual(data.stat, [0.1, 0.2, 0.3, 0.4])
        self.assertEqual(data.syst, [0.2, 0.2, 0.4, 0.4])

        self.assertEqual(data.var_up("tes"), [-7, -7, -7, -7])
        self.assertEqual(data.var_down("tes"), [-5, -7, -9, -11])

        self.assertEqual(data.var_up("jes"), [-5, -7, -10, -12])
        self.assertEqual(data.var_down("jes"), [-7, -7, -6, -6])

        self.assertEqual(data.var_up("theory"), [-7, -9, -11, -13])
        self.assertEqual(data.var_down("theory"), [-3, -1, 1, 3])

    ####### Neg
    def test_neg(self):
        """Check that -Yield inverts base and variations"""
        data = Yield([0, 3, 2, 1], [0.1, 0.2, 0.2, 0.1], [0.2, 0.3, 0.3, 0.3],
                     var_up={"jer": [1, 2, 2, 1], "theory": [-2, -4, -6, -8]},
                     var_down={"jes": [1, 1, 1, 1], "theory": [1, 2, 3, 4]})

        data = -data

        self.assertEqual(data.base, [-0, -3, -2, -1])
        self.assertEqual(data.stat, [0.1, 0.2, 0.2, 0.1])
        self.assertEqual(data.syst, [0.2, 0.3, 0.3, 0.3])
        self.assertEqual(data.var_up("jer"), [-1, -2, -2, -1])
        self.assertEqual(data.var_up("theory"), [2, 4, 6, 8])
        self.assertEqual(data.var_down("jes"), [-1, -1, -1, -1])
        self.assertEqual(data.var_down("theory"), [-1, -2, -3, -4])

    ####### Pos
    def test_pos(self):
        """Check that +Yield returns base and variations"""
        data = Yield([0, 3, 2, 1], [0.1, 0.2, 0.2, 0.1], [0.2, 0.3, 0.3, 0.3],
                     var_up={"jer": [1, 2, 2, 1], "theory": [-2, -4, -6, -8]},
                     var_down={"jes": [1, 1, 1, 1], "theory": [1, 2, 3, 4]})

        data = +data

        self.assertEqual(data.base, [0, 3, 2, 1])
        self.assertEqual(data.stat, [0.1, 0.2, 0.2, 0.1])
        self.assertEqual(data.syst, [0.2, 0.3, 0.3, 0.3])
        self.assertEqual(data.var_up("jer"), [1, 2, 2, 1])
        self.assertEqual(data.var_up("theory"), [-2, -4, -6, -8])
        self.assertEqual(data.var_down("jes"), [1, 1, 1, 1])
        self.assertEqual(data.var_down("theory"), [1, 2, 3, 4])

    ####### Len
    def test_len(self):
        """Check that len returns the length of the base"""
        data = Yield([0, 3, 2, 1])
        self.assertEqual(len(data), 4)

    ####### getitem
    def test_getitem(self):
        """Check that getitem returns an element of base"""
        data = Yield([0, 3, 2, 1])

        self.assertEqual(data[0], 0)
        self.assertEqual(data[1], 3)
        self.assertEqual(data[2], 2)
        self.assertEqual(data[3], 1)

    def test_getitem_index(self):
        """Check that an Error is raised if the index is invalid"""
        data = Yield([0, 3, 2, 1])
        self.assertRaises(IndexError, lambda: data[4])

    def test_getitem_convert(self):
        """Check that a yield object can be iterated"""
        data = Yield([0, 3, 2, 1])

        self.assertEqual(list(data), [0, 3, 2, 1])

    ####### mul
    def test_mul_number(self):
        """Check the result of multiplying a number with a yield"""
        data = Yield([1, 2, 3, 4], [0.1, 0.2, 0.3, 0.4], [0.2, 0.2, 0.4, 0.4],
                     var_up={"tes": [2, 2, 2, 2], "theory": [2, 4, 6, 8]},
                     var_down={"jes": [2, 2, 1, 1], "theory": [-2, -4, -6, -8]})

        data = data * (-2)
        self.assertEqual(data.base, [-2, -4, -6, -8])
        self.assertEqual(data.stat, [0.2, 0.4, 0.6, 0.8])
        self.assertEqual(data.syst, [0.4, 0.4, 0.8, 0.8])

        self.assertEqual(data.var_up("tes"), [-4, -4, -4, -4])
        self.assertEqual(data.var_down("tes"), [0, -4, -8, -12])

        self.assertEqual(data.var_up("jes"), [-0, -4, -10, -14])
        self.assertEqual(data.var_down("jes"), [-4, -4, -2, -2])

        self.assertEqual(data.var_up("theory"), [-4, -8, -12, -16])
        self.assertEqual(data.var_down("theory"), [4, 8, 12, 16])

    def test_mul_number_no_unert(self):
        """Check the result of multiplying a number with a yield"""
        data = Yield([1, 2, 3, 4])

        data = data * (-2)
        self.assertEqual(data.base, [-2, -4, -6, -8])
        self.assertIsNone(data._stat)
        self.assertIsNone(data._syst)

    def test_mul_yield(self):
        """Check the result of multiplying two yields"""
        data_a = Yield([1, 2, 3, 4], [0.1, 0.2, 0.3, 0.4], [0.2, 0.2, 0.4, 0.4],
                       var_up={"tes": [2, 2, 2, 2],
                               "theory": [2, 4, 6, 8]},
                       var_down={"jes": [2, 2, 1, 1],
                                 "theory": [-2, -4, -6, -8]})

        data_b = Yield([0, 3, 2, 1], [0.1, 0.2, 0.2, 0.1], [0.2, 0.3, 0.3, 0.3],
                       var_up={"jer": [1, 2, 2, 1],
                               "theory": [2, 4, 6, 8]},
                       var_down={"jes": [1, 1, 1, 1],
                                 "theory": [-1, -2, -3, -4]})

        data = data_a * data_b
        self.assertEqual(data.base, [0, 6, 6, 4])
        self.assertListAlmostEqual([x**2 for x in data.stat],
                                   [0.01, 0.52, 0.72, 0.32])
        self.assertListAlmostEqual([x**2 for x in data.syst],
                                   [0.04, 0.72, 1.45, 1.60])

        self.assertEqual(data.var_up("tes"), [0, 6, 4, 2])
        self.assertEqual(data.var_down("tes"), [0, 6, 8, 6])

        self.assertEqual(data.var_up("jes"), [0, 10, 15, 7])
        self.assertEqual(data.var_down("jes"), [2, 2, 1, 1])

        self.assertEqual(data.var_up("jer"), [1, 4, 6, 4])
        self.assertEqual(data.var_down("jer"), [-1, 8, 6, 4])

        self.assertEqual(data.var_up("theory"), [4, 16, 36, 64])
        self.assertEqual(data.var_down("theory"), [2, 8, 18, 32])

    def test_mul_no_uncert_self(self):
        """Check muling yields without self uncertainty"""
        data_a = Yield([1, 2, 3, 4])

        data_b = Yield([0, 3, 2, 1], [0.1, 0.2, 0.2, 0.1], [0.2, 0.3, 0.3, 0.3],
                       var_up={"jer": [1, 2, 2, 1],
                               "theory": [2, 4, 6, 8]},
                       var_down={"jes": [1, 1, 1, 1],
                                 "theory": [-1, -2, -3, -4]})

        data = data_a * data_b
        self.assertEqual(data.base, [0, 6, 6, 4])
        self.assertListAlmostEqual(data.stat, [0.1, 0.4, 0.6, 0.4])
        self.assertListAlmostEqual(data.syst, [0.2, 0.6, 0.9, 1.2])

        self.assertEqual(data.var_up("jes"), [-1, 10, 9, 4])
        self.assertEqual(data.var_down("jes"), [1, 2, 3, 4])

        self.assertEqual(data.var_up("jer"), [1, 4, 6, 4])
        self.assertEqual(data.var_down("jer"), [-1, 8, 6, 4])

        self.assertEqual(data.var_up("theory"), [2, 8, 18, 32])
        self.assertEqual(data.var_down("theory"), [-1, -4, -9, -16])

    def test_mul_no_uncert_other(self):
        data_a = Yield([1, 2, 3, 4])

        data_b = Yield([0, 3, 2, 1], [0.1, 0.2, 0.2, 0.1], [0.2, 0.3, 0.3, 0.3],
                       var_up={"jer": [1, 2, 2, 1],
                               "theory": [2, 4, 6, 8]},
                       var_down={"jes": [1, 1, 1, 1],
                                 "theory": [-1, -2, -3, -4]})

        data = data_b * data_a
        self.assertEqual(data.base, [0, 6, 6, 4])
        self.assertListAlmostEqual(data.stat, [0.1, 0.4, 0.6, 0.4])
        self.assertListAlmostEqual(data.syst, [0.2, 0.6, 0.9, 1.2])

        self.assertEqual(data.var_up("jes"), [-1, 10, 9, 4])
        self.assertEqual(data.var_down("jes"), [1, 2, 3, 4])

        self.assertEqual(data.var_up("jer"), [1, 4, 6, 4])
        self.assertEqual(data.var_down("jer"), [-1, 8, 6, 4])

        self.assertEqual(data.var_up("theory"), [2, 8, 18, 32])
        self.assertEqual(data.var_down("theory"), [-1, -4, -9, -16])

    def test_mul_different_bin_count(self):
        """Check that a value error is raised if the bin count differs"""
        data_a = Yield([1, 2, 3, 4])
        data_b = Yield([0, 3, 2, 1, 5])

        self.assertRaises(ValueError, lambda: data_a * data_b)

    ####### rmul
    def test_rmul_number(self):
        """Check the result of multiplying a number with a yield"""
        data = Yield([1, 2, 3, 4], [0.1, 0.2, 0.3, 0.4], [0.2, 0.2, 0.4, 0.4],
                     var_up={"tes": [2, 2, 2, 2], "theory": [2, 4, 6, 8]},
                     var_down={"jes": [2, 2, 1, 1], "theory": [-2, -4, -6, -8]})

        data = -2 * data
        self.assertEqual(data.base, [-2, -4, -6, -8])
        self.assertEqual(data.stat, [0.2, 0.4, 0.6, 0.8])
        self.assertEqual(data.syst, [0.4, 0.4, 0.8, 0.8])

        self.assertEqual(data.var_up("tes"), [-4, -4, -4, -4])
        self.assertEqual(data.var_down("tes"), [0, -4, -8, -12])

        self.assertEqual(data.var_up("jes"), [-0, -4, -10, -14])
        self.assertEqual(data.var_down("jes"), [-4, -4, -2, -2])

        self.assertEqual(data.var_up("theory"), [-4, -8, -12, -16])
        self.assertEqual(data.var_down("theory"), [4, 8, 12, 16])

    ####### rebin
    def test_rebin(self):
        """Check the rebinning a yield sums adjacent bins"""
        data = Yield([1, 2, 3, 4], [0.1, 0.2, 0.3, 0.4], [0.2, 0.2, 0.4, 0.4],
                     var_up={"tes": [2, 2, 2, 2], "theory": [2, 4, 6, 8]},
                     var_down={"jes": [2, 2, 1, 1], "theory": [-2, -4, -6, -8]})

        data = data.rebin([0, 1, 2], [0, 2])
        self.assertEqual(data.base, [1, 5, 4])
        self.assertListAlmostEqual([x**2 for x in data.stat], [0.01, 0.13, 0.16])
        self.assertListAlmostEqual([x**2 for x in data.syst], [0.04, 0.20, 0.16])

        self.assertEqual(data.var_up("tes"), [2, 4, 2])
        self.assertEqual(data.var_down("tes"), [0, 6, 6])

        self.assertEqual(data.var_up("jes"), [0, 7, 7])
        self.assertEqual(data.var_down("jes"), [2, 3, 1])

        self.assertEqual(data.var_up("theory"), [2, 10, 8])
        self.assertEqual(data.var_down("theory"), [-2, -10, -8])

    ####### truediv
    def test_truediv_number(self):
        """Check the result of dividing a number with a yield"""
        data = Yield([1, 2, 3, 4], [0.1, 0.2, 0.3, 0.4], [0.2, 0.2, 0.4, 0.4],
                     var_up={"tes": [2, 2, 2, 2], "theory": [2, 4, 6, 8]},
                     var_down={"jes": [2, 2, 1, 1], "theory": [-2, -4, -6, -8]})

        data = data / (-2)
        self.assertEqual(data.base, [-0.5, -1, -1.5, -2])
        self.assertEqual(data.stat, [0.05, 0.1, 0.15, 0.2])
        self.assertEqual(data.syst, [0.1, 0.1, 0.2, 0.2])

        self.assertEqual(data.var_up("tes"), [-1, -1, -1, -1])
        self.assertEqual(data.var_down("tes"), [0, -1, -2, -3])

        self.assertEqual(data.var_up("jes"), [0, -1, -2.5, -3.5])
        self.assertEqual(data.var_down("jes"), [-1, -1, -0.5, -0.5])

        self.assertEqual(data.var_up("theory"), [-1, -2, -3, -4])
        self.assertEqual(data.var_down("theory"), [1, 2, 3, 4])

    def test_truediv_number_no_unert(self):
        """Check the result of multiplying a number with a yield"""
        data = Yield([1, 2, 3, 4])

        data = data / (-2)
        self.assertEqual(data.base, [-0.5, -1, -1.5, -2])
        self.assertIsNone(data._stat)
        self.assertIsNone(data._syst)

    def test_truediv_yield(self):
        """Check the result of dividing two yields"""
        data_a = Yield([1, 2, 3, 4], [0.1, 0.2, 0.3, 0.4], [0.2, 0.2, 0.4, 0.4],
                       var_up={"tes": [2, 2, 2, 2],
                               "theory": [2, 4, 6, 8]},
                       var_down={"jes": [2, 2, 1, 1],
                                 "theory": [-2, -4, -6, -8]})

        data_b = Yield([1, 3, 2, 1], [0.1, 0.2, 0.2, 0.1], [0.2, 0.3, 0.3, 0.3],
                       var_up={"jer": [1, 2, 2, 1],
                               "theory": [2, 4, 6, 8]},
                       var_down={"jes": [1, 1, 1, 1],
                                 "theory": [-1, -2, -3, -4]})

        data = data_a / data_b
        self.assertListAlmostEqual(data.base, [1, 2/3, 1.5, 4])
        self.assertListAlmostEqual([x**2 for x in data.stat],
                                   [0.02, 0.52/81, 0.045, 0.32]) 
        self.assertListAlmostEqual([x**2 for x in data.syst],
                                   [0.08, 0.08/9, 1.45/16, 1.6])

        self.assertEqual(data.var_up("tes"), [2, 2/3, 1, 2])
        self.assertEqual(data.var_down("tes"), [0, 2/3, 2, 6])

        self.assertEqual(data.var_up("jes"), [0, 0.4, 5/3, 7])
        self.assertEqual(data.var_down("jes"), [2, 2, 1, 1])

        self.assertEqual(data.var_up("jer"), [1, 1, 3/2, 4])
        self.assertEqual(data.var_down("jer"), [1, 0.5, 3/2, 4])

        self.assertEqual(data.var_up("theory"), [1, 1, 1, 1])
        self.assertEqual(data.var_down("theory"), [2, 2, 2, 2])

    def test_truediv_no_uncert_self(self):
        """Check divison yields without self uncertainty"""
        data_a = Yield([1, 2, 3, 4])

        data_b = Yield([1, 3, 2, 1], [0.1, 0.2, 0.2, 0.1], [0.2, 0.3, 0.3, 0.3],
                       var_up={"jer": [1, 2, 2, 1],
                               "theory": [2, 4, 6, 8]},
                       var_down={"jes": [1, 1, 1, 1],
                                 "theory": [-1, -2, -3, -4]})

        data = data_a / data_b
        self.assertEqual(data.base, [1, 2/3, 1.5, 4])
        self.assertListAlmostEqual([x**2 for x in data.stat],
                                   [0.01, 0.16/81, 0.09/4, 0.16])
        self.assertListAlmostEqual([x**2 for x in data.syst],
                                   [0.04, 0.04/9, 0.81/16, 1.44])

        self.assertEqual(data.var_up("jes"), [1, 0.4, 1, 4])
        self.assertEqual(data.var_down("jes"), [1, 2, 3, 4])

        self.assertEqual(data.var_up("jer"), [1, 1, 1.5, 4])
        self.assertEqual(data.var_down("jer"), [1, 0.5, 1.5, 4])

        self.assertEqual(data.var_up("theory"), [0.5, 0.5, 0.5, 0.5])
        self.assertEqual(data.var_down("theory"), [-1, -1, -1, -1])

    def test_truediv_no_uncert_other(self):
        """Check division without other uncertainties"""
        data_b = Yield([1, 3, 2, 1], [0.1, 0.2, 0.2, 0.1], [0.2, 0.3, 0.3, 0.3],
                       var_up={"jer": [1, 2, 2, 1],
                               "theory": [2, 4, 6, 8]},
                       var_down={"jes": [1, 1, 1, 1],
                                 "theory": [-1, -2, -3, -4]})

        data_a = Yield([1, 2, 3, 4])

        data = data_b / data_a
        self.assertEqual(data.base, [1, 3/2, 2/3, 0.25])
        self.assertListAlmostEqual(data.stat, [0.1, 0.1, 0.2/3, 0.025])
        self.assertListAlmostEqual(data.syst, [0.2, 0.3/2, 0.1, 0.3/4])

        self.assertEqual(data.var_up("jes"), [1, 2.5, 1, 0.25])
        self.assertEqual(data.var_down("jes"), [1, 0.5, 1/3, 0.25])

        self.assertEqual(data.var_up("jer"), [1, 1, 2/3, 0.25])
        self.assertEqual(data.var_down("jer"), [1, 2, 2/3, 0.25])

        self.assertEqual(data.var_up("theory"), [2, 2, 2, 2])
        self.assertEqual(data.var_down("theory"), [-1, -1, -1, -1])

    def test_truediv_different_bin_count(self):
        """Check that a value error is raised if the bin count differs"""
        data_a = Yield([1, 2, 3, 4])
        data_b = Yield([0, 3, 2, 1, 5])

        self.assertRaises(ValueError, lambda: data_a / data_b)

    def test_rtruediv_number_no_unert(self):
        """Check the result of multiplying a number with a yield"""
        data = Yield([1, 2, 3, 4])

        data = -2 / data
        self.assertEqual(data.base, [-2, -1, -2/3, -0.5])
        self.assertIsNone(data._stat)
        self.assertIsNone(data._syst)


    ####### total
    def test_total(self):
        """Check the total contains all values"""
        data = Yield([1, 2, 3, 4], [0.1, 0.2, 0.3, 0.4], [0.2, 0.2, 0.4, 0.4],
                     var_up={"tes": [2, 2, 2, 2], "theory": [2, 4, 6, 8]},
                     var_down={"jes": [2, 2, 1, 1], "theory": [-2, -4, -6, -8]})

        total = data.total()

        self.assertEqual(total.base[0], 10)
        self.assertAlmostEqual(total.stat[0]**2, 0.01+0.04+0.09+0.16)
        self.assertAlmostEqual(total.syst[0]**2, 0.04+0.04+0.16+0.16)

        self.assertEqual(total.var_up("jes"), [14])
        self.assertEqual(total.var_down("jes"), [6])

        self.assertEqual(total.var_up("tes"), [8])
        self.assertEqual(total.var_down("tes"), [12])

        self.assertEqual(total.var_up("theory"), [20])
        self.assertEqual(total.var_down("theory"), [-20])

    def test_sum(self):
        """Check the total contains all values"""
        data = Yield([1, 2, 3, 4], [0.1, 0.2, 0.3, 0.4], [0.2, 0.2, 0.4, 0.4],
                     var_up={"tes": [2, 2, 2, 2], "theory": [2, 4, 6, 8]},
                     var_down={"jes": [2, 2, 1, 1], "theory": [-2, -4, -6, -8]})

        total = data.sum()

        self.assertEqual(total, 10)


    ######## Vary
    def test_vary_simple(self):
        """Check that vary return up, down or base"""
        data = Yield([1, 2, 3, 4],
                     var_up={"var1": [1.1, 2, 3, 4],
                             "var2": [1, 2.1, 3, 4],
                             "var3": [1, 2.1, 3.1, 4]},
                     var_down={"var1": [0.8, 2, 3, 4],
                               "var2": [1, 1.8, 3, 4],
                               "var4": [1, 2, 3.2, 4.2]})

        self.assertListAlmostEqual(data.vary(), [1, 2, 3, 4])
        self.assertListAlmostEqual(data.vary(var1=1), [1.1, 2, 3, 4])
        self.assertListAlmostEqual(data.vary(var2=0), [1, 2, 3, 4])
        self.assertListAlmostEqual(data.vary(var3=-1), [1, 1.9, 2.9, 4])
        self.assertListAlmostEqual(data.vary(var4=1), [1, 2, 2.8, 3.8])
            
    def test_vary_interpolate(self):
        """Check that vary interpolates between -1 and 1"""
        data = Yield([1, 2, 3, 4],
                     var_up={"var1": [1.1, 2, 3, 4],
                             "var2": [1, 2.1, 3, 4],
                             "var3": [1, 2.1, 3.1, 4]},
                     var_down={"var1": [0.8, 2, 3, 4],
                               "var2": [1, 1.8, 3, 4],
                               "var4": [1, 2, 3.2, 4.2]})

        self.assertListAlmostEqual(data.vary(var1=0.5), [1.05, 2, 3, 4])
        self.assertListAlmostEqual(data.vary(var2=0.5), [1, 2.05, 3, 4])
        self.assertListAlmostEqual(data.vary(var3=-0.5), [1, 1.95, 2.95, 4])
        self.assertListAlmostEqual(data.vary(var4=0.5), [1, 2, 2.9, 3.9])
            
    def test_vary_extrapolate(self):
        """Check that vary extrapolate outside -1 and 1"""
        data = Yield([1, 2, 3, 4],
                     var_up={"var1": [1.1, 2, 3, 4],
                             "var2": [1, 2.1, 3, 4],
                             "var3": [1, 2.1, 3.1, 4]},
                     var_down={"var1": [0.8, 2, 3, 4],
                               "var2": [1, 1.8, 3, 4],
                               "var4": [1, 2, 3.2, 4.2]})

        self.assertListAlmostEqual(data.vary(var1=2), [1.2, 2, 3, 4])
        self.assertListAlmostEqual(data.vary(var2=2), [1, 2.2, 3, 4])
        self.assertListAlmostEqual(data.vary(var3=-2), [1, 1.8, 2.8, 4])
        self.assertListAlmostEqual(data.vary(var4=2), [1, 2, 2.6, 3.6])
            
    def test_vary_combine(self):
        """Check that vary combines multiple variations"""
        data = Yield([1, 2, 3, 4],
                     var_up={"var1": [1.1, 2, 3, 4],
                             "var2": [1, 2.1, 3, 4],
                             "var3": [1, 2.1, 3.1, 4]},
                     var_down={"var1": [0.8, 2, 3, 4],
                               "var2": [1, 1.8, 3, 4],
                               "var4": [1, 2, 3.2, 4.2]})

        self.assertListAlmostEqual(data.vary(var1=-1, var2=0.5, var3=1, var5=10),
                                   [0.8, 2.15, 3.1, 4])
