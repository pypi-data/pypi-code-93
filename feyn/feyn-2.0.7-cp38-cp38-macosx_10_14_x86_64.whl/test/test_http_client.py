from unittest import TestCase

from feyn._httpclient import iter_api_warnings


class TestIterAPIWarnings(TestCase):
    def test_should_report_nothing_for_empty_string(self):
        warnings = list(iter_api_warnings(""))
        self.assertEqual([], warnings)

    def test_should_report_warnings_from_dotted_component(self):
        warnings = list(iter_api_warnings("a.b.c \"oops...\""))
        self.assertEqual([("a.b.c", "oops...")], warnings)

    def test_should_report_complex_warning(self):
        warnings = list(iter_api_warnings("StressTest \"newline: \\n, tab: \\t, quote: \\\", backslash: \\\\.\""))
        expected = [
            ("StressTest", "newline: \n, tab: \t, quote: \", backslash: \\."),
        ]
        self.assertEqual(expected, warnings)

    def test_should_report_multiple_valid_warnings(self):
        warnings = list(iter_api_warnings("QLattice \"update your version of feyn\", Accounts \"pay your bills\""))
        expected = [
            ("QLattice", "update your version of feyn"),
            ("Accounts", "pay your bills"),
        ]
        self.assertEqual(expected, warnings)

    def test_should_skip_malformed_warning(self):
        header_string = "QLattice \"update your version of feyn\", <invalid warning!> Accounts \"pay your bills\""
        warnings = list(iter_api_warnings(header_string))
        expected = [
            ("QLattice", "update your version of feyn"),
            ("Accounts", "pay your bills"),
        ]
        self.assertEqual(expected, warnings)
