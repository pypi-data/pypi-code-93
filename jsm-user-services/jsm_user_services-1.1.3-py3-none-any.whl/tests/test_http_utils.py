from unittest import TestCase

from requests import exceptions

from jsm_user_services.support.http_utils import convert_header_to_meta_key
from jsm_user_services.support.http_utils import request


class TestContracts(TestCase):
    def test_should_raise_timeout(self):
        with request() as r:
            # check https://stackoverflow.com/a/100859 for the reason of "http://10.255.255.1/"
            self.assertRaises(exceptions.Timeout, r.get, "http://10.255.255.1")

    def test_should_convert_header_to_meta_key(self):
        header1 = "x-original-forwarded-for"
        header2 = "authentication"
        header3 = "x-forwarded-for"

        self.assertEqual(convert_header_to_meta_key(header1), "HTTP_X_ORIGINAL_FORWARDED_FOR")
        self.assertEqual(convert_header_to_meta_key(header2), "HTTP_AUTHENTICATION")
        self.assertEqual(convert_header_to_meta_key(header3), "HTTP_X_FORWARDED_FOR")
