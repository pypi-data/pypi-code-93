"""Tests for trading.datasets.utils.string_utils."""
# pylint: disable=missing-class-docstring,missing-function-docstring

from trading.datasets.utils import string_utils


class TestStringUtils:

    def test_special_chars_to_words(self):
        assert string_utils.special_chars_to_words(
            'shawarma_') == 'shawarma[UNDERSCORE]'
        assert string_utils.special_chars_to_words(
            '!$@') == '[EXCLAMATION][DOLLAR][AT]'

    def test_special_words_to_chars(self):
        assert string_utils.special_words_to_chars(
            'shawarma[UNDERSCORE]') == 'shawarma_'
        assert string_utils.special_words_to_chars(
            '[EXCLAMATION][DOLLAR][AT]') == '!$@'

    def test_digitlen(self):
        assert string_utils.digitlen(0) == 1
        assert string_utils.digitlen(None) == 0
        assert string_utils.digitlen(3124) == 4
        assert string_utils.digitlen(-3124) == 5
        assert string_utils.digitlen(-31240999) == 9
