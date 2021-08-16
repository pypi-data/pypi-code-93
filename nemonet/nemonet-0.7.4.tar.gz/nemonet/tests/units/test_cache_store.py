import unittest
from nemonet.engines.cache_store import KeyValueStore

class CachingTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.key_value_Store = KeyValueStore()

    def tearDown(self) -> None:
        self.key_value_Store.close()

    def test_add_get(self):
        self.key_value_Store.add("key","value")
        value = self.key_value_Store.get_value_as_str("key")
        self.assertTrue( value == "value" )

    def test_add_get_aigu(self):
        self.key_value_Store.add("key","valeé")
        value = self.key_value_Store.get_value_as_str("key")
        self.assertTrue( value == "valeé" )

    def test_add_get_umlaut(self):
        self.key_value_Store.add("key","valö")
        value = self.key_value_Store.get_value_as_str("key")
        self.assertTrue( value == "valö" )

    def test_add_get_grave(self):
        self.key_value_Store.add("key","valè")
        value = self.key_value_Store.get_value_as_str("key")
        self.assertTrue( value == "valè" )

    def test_add_get_circonflexe(self):
        self.key_value_Store.add("key","valèç")
        value = self.key_value_Store.get_value_as_str("key")
        self.assertTrue( value == "valèç" )


if __name__ == '__main__':
    unittest.main()
