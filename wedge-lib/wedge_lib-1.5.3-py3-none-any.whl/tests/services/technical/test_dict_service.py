from w.services.technical.dict_service import DictService
from w.tests.mixins.testcase_mixin import TestCaseMixin


class TestDictService(TestCaseMixin):
    @classmethod
    def setup_class(cls):
        cls.data = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
            "key4": "value4",
        }

    """
    keep_keys
    """

    def test_keep_keys_with_no_key_found_return_dict(self):
        """ Ensure method succeed even if all keys to keep do not exist """
        actual = DictService.keep_keys(self.data, ["unknown1", "unknown2"])
        assert actual == {}

    def test_keep_keys_with_success_return_dict(self):
        """ Ensure method succeed """
        actual = DictService.keep_keys(
            self.data, ["value1", "key2", "unknown2", "key4"]
        )
        self.assert_equals_resultset(actual)

    """
    remove_keys
    """

    def test_remove_keys_with_no_key_found_return_dict(self):
        """ Ensure method succeed even if all keys to remove do not exist """
        actual = DictService.remove_keys(self.data, ["unknown1", "unknown2"])
        self.assert_equals_resultset(actual)

    def test_remove_keys_with_success_return_dict(self):
        """ Ensure method succeed """
        actual = DictService.remove_keys(
            self.data, ["value1", "key2", "unknown2", "key4"]
        )
        self.assert_equals_resultset(actual)

    """
    get_last_entry_value
    """

    def test_get_last_entry_value_with_success_return_dict(self):
        """ Ensure method succeed """
        actual = DictService.get_last_entry_value(self.data)
        self.assert_equals_resultset(actual)

    """
    remap_keys
    """

    def test_remap_keys_with_success_return_dict(self):
        """ Ensure method succeed """
        remap_keys = {
            "key1": "remap-key1",
            "key3": "remap-key3",
            "key4": "remap-key4",
        }
        actual = DictService.remap_keys(self.data, remap_keys)
        self.assert_equals_resultset(actual)
