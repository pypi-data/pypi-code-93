import unittest

from appyx.layers.interface.validators.dict_validator import DictValidator


class DictValidatorTest(unittest.TestCase):
    def test_empty_dict_has_keys_included(self):
        dictionary = {}
        validator = DictValidator()

        result = validator.validate_keys_included_in(dictionary, [])

        self.assertTrue(result.is_successful())

    def test_dict_has_keys_included(self):
        dictionary = {'key1': 'value1'}
        validator = DictValidator()

        result = validator.validate_keys_included_in(dictionary, ['key1', 'key2'])

        self.assertTrue(result.is_successful())

    def test_when_dict_has_keys_not_included_an_error_is_answered(self):
        dictionary = {'key3': 'value1'}
        validator = DictValidator()

        result = validator.validate_keys_included_in(dictionary, ['key1', 'key2'])

        self.assertTrue(result.has_errors())
        self.assertTrue(result.has_error_with_code('simple_error_code'))
        self.assertEqual(result.errors()[0].text(), 'Key key3 is not included in [\'key1\', \'key2\']')
