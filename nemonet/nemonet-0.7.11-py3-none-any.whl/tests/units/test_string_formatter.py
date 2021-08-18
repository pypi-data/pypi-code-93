import unittest
from nemonet.engines.cache_store import KeyValueStore

class StringReformatTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.cache = KeyValueStore()
        self.cache.add('cu_2','cx_2')
        self.cache.add('cu_3','cx_3')

    def tearDown(self) -> None:
        self.cache.close()

    def test_string_formatter_use_case_1(self):
        self.assertTrue(self.cache.replace_formated_key("https://jqueryui.com/#{cu_2}/#{cu_3}") == 'https://jqueryui.com/cx_2/cx_3')

    def test_string_formatter_use_case_2(self):
        self.assertTrue(self.cache.replace_formated_key("https://jqueryui.com/#{cu_3}/#{cu_2}") == 'https://jqueryui.com/cx_3/cx_2')

    def test_string_formatter_key_not_in_cache(self):
        with self.assertRaises(KeyError):
            self.cache.replace_formated_key("https://jqueryui.com/#{cu_4}/#{cu_5}")

    def test_string_formatter_only_one_valid_key(self):
        self.assertTrue(self.cache.replace_formated_key("https://jqueryui.com/#{cu_3}/#cu_2}") == 'https://jqueryui.com/cx_3/#cu_2}')


if __name__ == '__main__':
    unittest.main()
