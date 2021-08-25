import urllib

from django import test
from ievv_opensource.ievv_i18n_url.base_url import BaseUrl


@test.override_settings(IEVV_I18N_URL_FALLBACK_BASE_URL='https://www.example.com')
class TestBaseUrl(test.TestCase):
    def test_parsed_url_none(self):
        self.assertEqual(BaseUrl().parsed_url.geturl(), 'https://www.example.com')

    def test_parsed_url_string(self):
        self.assertEqual(BaseUrl('https://string.example.com/x/y').parsed_url.geturl(), 'https://string.example.com')

    def test_parsed_url_parseresult(self):
        self.assertEqual(BaseUrl(urllib.parse.urlparse('https://parsed.example.com/x/y')).parsed_url.geturl(), 'https://parsed.example.com')

    def test_scheme(self):
        self.assertEqual(BaseUrl('https://example.com').scheme, 'https')
        self.assertEqual(BaseUrl('http://example.com').scheme, 'http')

    def test_netloc(self):
        self.assertEqual(BaseUrl('https://example.com').netloc, 'example.com')
        self.assertEqual(BaseUrl('https://example.com:8080').netloc, 'example.com:8080')

    def test_hostname(self):
        self.assertEqual(BaseUrl('https://example.com').hostname, 'example.com')
        self.assertEqual(BaseUrl('https://example.com:8080').hostname, 'example.com')

    def test_port(self):
        self.assertEqual(BaseUrl('https://example.com').port, None)
        self.assertEqual(BaseUrl('https://example.com:8080').port, 8080)

    def test_build_absolute_url(self):
        self.assertEqual(
            BaseUrl('https://example.com').build_absolute_url('/my/path?x=2'),
            'https://example.com/my/path?x=2')
        self.assertEqual(
            BaseUrl('https://example.com/a/b').build_absolute_url('/my/path?x=2'),
            'https://example.com/my/path?x=2')
        self.assertEqual(
            BaseUrl('https://example.com').build_absolute_url('https://other.example.com/a/b'),
            'https://other.example.com/a/b')
