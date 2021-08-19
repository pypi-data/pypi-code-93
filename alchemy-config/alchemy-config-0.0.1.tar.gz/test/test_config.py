#*****************************************************************#
# (C) Copyright IBM Corporation 2020.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
#*****************************************************************#
'''Test the methods of the Config class.
'''

import copy
import json
import os
import re
import unittest

import yaml

import aconfig

from . import fixtures


# Unit tests #######################################################################################

class TestConfig(unittest.TestCase):
    '''Test methods of Config class.
    '''
    def test__init__pass(self):
        '''Test __init__ function passes.
        '''
        good_yaml = aconfig.Config.from_yaml(fixtures.GOOD_CONFIG_LOCATION)
        self.assertIsInstance(good_yaml, aconfig.Config)

    def test__verify_config_location_fail(self):
        '''Test _verify_config_location throws correct exceptions.
        '''
        # tests not-a-string error
        with self.assertRaises(AssertionError) as ex1:
            bad_config1 = aconfig.Config._verify_config_location(['not', 'a', 'string', '!'])
        raised_exception1 = ex1.exception
        self.assertIsInstance(raised_exception1, AssertionError)
        # make sure bad_config1 was NOT initialized
        self.assertEqual(getattr(locals(), 'bad_config1', None), None)

        # tests a bad-location error
        with self.assertRaises(AssertionError) as ex2:
            bad_config2 = aconfig.Config._verify_config_location(fixtures.BAD_CONFIG_LOCATION)
        raised_exception2 = ex2.exception
        self.assertIsInstance(raised_exception2, AssertionError)
        # make sure bad_config2 was NOT initialized
        self.assertEqual(getattr(locals(), 'bad_config2', None), None)

        # tests a non-config-file error
        with self.assertRaises(AssertionError) as ex3:
            bad_config3 = aconfig.Config._verify_config_location(fixtures.NOT_YAML_CONFIG_LOCATION)
        raised_exception3 = ex3.exception
        self.assertIsInstance(raised_exception3, AssertionError)
        # make sure bad_config3 was NOT initialized
        self.assertEqual(getattr(locals(), 'bad_config3', None), None)

    def test__load_yaml_file_pass(self):
        '''Test _load_yaml_file passes. By the time it gets here, the file location has been verified
        '''
        loaded_yaml = aconfig.Config._load_yaml_file(fixtures.GOOD_CONFIG_LOCATION)
        self.assertIsInstance(loaded_yaml, dict)

    def test__load_yaml_file_fail(self):
        '''Overkill test here -- should never be reached, but checking it will fail just in case.
        '''
        with self.assertRaises(Exception) as ex1:
            bad_yaml1 = aconfig.Config._load_yaml_file(fixtures.BAD_CONFIG_LOCATION)
        raised_exception1 = ex1.exception
        self.assertIsInstance(raised_exception1, Exception)
        # make sure bad_yaml1 was NOT initialized
        self.assertEqual(getattr(locals(), 'bad_yaml1', None), None)

        with self.assertRaises(Exception) as ex2:
            bad_yaml2 = aconfig.Config._load_yaml_file(fixtures.NOT_YAML_CONFIG_LOCATION)
        raised_exception2 = ex2.exception
        self.assertIsInstance(raised_exception2, Exception)
        # make sure bad_yaml2 was NOT initialized
        self.assertEqual(getattr(locals(), 'bad_yaml2', None), None)

    def test__eval_value_pass(self):
        '''Test passes all known converted types if pass in a Python str.
        '''
        # int
        test_zero_int = aconfig.Config._eval_value('0')
        test_small_int = aconfig.Config._eval_value('1')
        test_big_int = aconfig.Config._eval_value('1000000000')
        test_negative_int = aconfig.Config._eval_value('-10')

        self.assertEqual(test_zero_int, 0)
        self.assertEqual(test_small_int, 1)
        self.assertEqual(test_big_int, 1000000000)
        self.assertEqual(test_negative_int, -10)

        # bool
        test_True = aconfig.Config._eval_value('True')
        test_true = aconfig.Config._eval_value('true')
        test_False = aconfig.Config._eval_value('False')
        test_false = aconfig.Config._eval_value('false')

        self.assertEqual(test_True, True)
        self.assertEqual(test_true, True)
        self.assertEqual(test_False, False)
        self.assertEqual(test_false, False)

        # float
        test_zero_float = aconfig.Config._eval_value('0.0')
        test_small_float = aconfig.Config._eval_value('0.0001')
        test_super_small_float = aconfig.Config._eval_value('0.000000000000000000000000001')
        test_big_float = aconfig.Config._eval_value('1000000000.1')
        test_negative_float = aconfig.Config._eval_value('-10.01')

        self.assertEqual(test_zero_float, 0.0)
        self.assertEqual(test_small_float, 0.0001)
        self.assertEqual(test_super_small_float, 0.000000000000000000000000001)
        self.assertEqual(test_big_float, 1000000000.1)
        self.assertEqual(test_negative_float, -10.01)

        # str
        zero_str = ''
        small_str = 'small'
        big_str = 'this\nis supposed\tto be\r "a" --long-- =+{]{][{)(****.string\n\\n\n\n!!'
        whitespace_str = ' \r \t \n\n'
        test_zero_str = aconfig.Config._eval_value(zero_str)
        test_small_str = aconfig.Config._eval_value(small_str)
        test_big_str = aconfig.Config._eval_value(big_str)
        test_whitespace_str = aconfig.Config._eval_value(whitespace_str)

        self.assertEqual(test_zero_str, zero_str)
        self.assertEqual(test_small_str, small_str)
        self.assertEqual(test_big_str, big_str)
        self.assertEqual(test_whitespace_str, zero_str) # NOTE THAT WE TEST AGAINST zero_str !!!!

    def test__eval_value_fail(self):
        '''Test fails if you don't pass in Python str.
        '''
        with self.assertRaises(TypeError) as ex1:
            bad_val1 = aconfig.Config._eval_value(None)
        raised_exception1 = ex1.exception
        self.assertIsInstance(raised_exception1, TypeError)
        # make sure bad_val1 was NOT initialized
        self.assertEqual(getattr(locals(), 'bad_val1', None), None)

        with self.assertRaises(Exception) as ex2:
            bad_val2 = aconfig.Config._eval_value(10)
        raised_exception2 = ex2.exception
        self.assertIsInstance(raised_exception2, TypeError)
        # make sure bad_val2 was NOT initialized
        self.assertEqual(getattr(locals(), 'bad_val2', None), None)

    def test__update_with_env_vars_pass(self):
        '''Test config can be overriden by env vars
        '''
        good_yaml = aconfig.Config.from_yaml(fixtures.GOOD_CONFIG_LOCATION)

        # test it is not the desired value yet
        self.assertNotEqual(good_yaml.key1.key2.int_key, 123454321)

        # set an environment variable; must be upper-case
        os.environ['KEY1_KEY2_INT_KEY'] = '123454321'
        # should NOT set this value -- the test would fail in this case
        os.environ['key1_key2_int_key'] = '9876'

        # test that environment variable is set; a little wonky here...
        good_yaml = aconfig.Config._update_with_env_vars(good_yaml, good_yaml)

        # should be desired value now
        self.assertEqual(good_yaml.key1.key2.int_key, 123454321)

    def test__env_var_from_key_pass(self):
        '''Test that the class correctly converts to env-var-like keys (all caps, _ separated)
        '''
        test_key1 = 'key-1'
        key1 = 'KEY_1'
        test_key2 = 'key.2'
        key2 = 'KEY_2'
        test_key3 = '.key.-3-'
        key3 = '_KEY__3_'
        test_key4 = '__KEY_4__'
        key4 = '__KEY_4__'

        obj = lambda _:_
        obj._search_pattern = re.compile(r'[.-]')

        self.assertEqual(aconfig.Config._env_var_from_key(obj, test_key1), key1)
        self.assertEqual(aconfig.Config._env_var_from_key(obj, test_key2), key2)
        self.assertEqual(aconfig.Config._env_var_from_key(obj, test_key3), key3)
        self.assertEqual(aconfig.Config._env_var_from_key(obj, test_key4), key4)

    def test_method_names_allowed_as_key(self):
        '''Methods on self should be allowed as keys in config.
        '''
        config = {
            '_env_var_from_key': 1,
            '__init__': 2
        }
        c = aconfig.Config(config)
        self.assertIn('__init__', c)
        self.assertEqual(c['__init__'], 2)

    def test_dicts_in_lists(self):
        '''Test that dicts inside of lists are recursively converted to Config
        objects
        '''
        cfg = aconfig.Config({'a': {'b': [{'c': 1}]}})
        self.assertEqual(cfg.a.b[0].c, 1)

    def test_deepcopy(self):
        '''Test that copy.deepcopy can be used on a Config object
        '''
        cfg = aconfig.Config({'a': {'b': [{'c': 1}]}})
        cfg_copy = copy.deepcopy(cfg)
        self.assertEqual(
            json.dumps(cfg, sort_keys=True),
            json.dumps(cfg_copy, sort_keys=True))
        cfg_copy.a.b[0].c = 2
        self.assertEqual(cfg.a.b[0].c, 1)
        self.assertEqual(cfg_copy.a.b[0].c, 2)

    def test_yaml_dump(self):
        '''Test yaml.dump(config) works'''
        loaded_yaml = aconfig.Config.from_yaml(fixtures.GOOD_CONFIG_LOCATION)

        # Dump both safe and non-safe
        yaml_dump = yaml.dump(loaded_yaml)
        yaml_safe_dump = yaml.safe_dump(loaded_yaml)
        assert yaml_dump == yaml_safe_dump

        # Load both ways
        yaml_loaded = yaml.load(yaml_dump)
        yaml_safe_loaded = yaml.safe_load(yaml_dump)
        assert yaml_loaded == yaml_safe_loaded
