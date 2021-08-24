import logging
from io import StringIO

from django.http import HttpResponse
from django.test import TestCase

import eventy.config
import eventy.config.django
from eventy.logging import SimpleHandler


class TestCorrelationId(TestCase):

    def test_hello_generate_correlation_id(self):
        response: HttpResponse = self.client.get('/hello')
        self.assertEqual(response.status_code, 200)
        self.assertRegex(response.json()['hello'], "eventy-django-test:GET_/hello:.*")

    def test_hello_propagate_correlation_id(self):
        """
        NOTE: I didn't find any way to pass arbitrary headers to self.client (django.test.client.Client)

        See: run_integration_test.sh
        """

    def test_health(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)


class TestAccessLogging(TestCase):
    def setUp(self) -> None:
        self.log_string_io = StringIO()
        self.log_handler = SimpleHandler(colored=False, level='INFO')
        self.log_handler.stream = self.log_string_io
        logging.getLogger().addHandler(self.log_handler)

    def test_health_enable_logging(self):
        eventy.config.django.DJANGO_ACCESS_DISABLE_HEALTH_LOGGING = False

        self.client.get('/health')
        self.client.get('/hello')
        self.assertRegex(self.log_string_io.getvalue(), 'Request: GET /health')
        self.assertRegex(self.log_string_io.getvalue(), 'Response: GET /health')
        self.assertRegex(self.log_string_io.getvalue(), 'Request: GET /hello')
        self.assertRegex(self.log_string_io.getvalue(), 'Response: GET /hello')

    def test_health_disable_logging(self):
        eventy.config.django.DJANGO_ACCESS_DISABLE_HEALTH_LOGGING = True

        self.client.get('/health')
        self.client.get('/hello')
        self.assertNotRegex(self.log_string_io.getvalue(), 'Request: GET /health')
        self.assertNotRegex(self.log_string_io.getvalue(), 'Response: GET /health')
        self.assertRegex(self.log_string_io.getvalue(), 'Request: GET /hello')
        self.assertRegex(self.log_string_io.getvalue(), 'Response: GET /hello')

