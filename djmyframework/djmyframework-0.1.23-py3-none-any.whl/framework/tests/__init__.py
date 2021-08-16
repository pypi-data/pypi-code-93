# Create your tests here.
import json

from django.conf import settings
from django.test import RequestFactory, TestCase

class BaseTestCase(TestCase):


    databases = '__all__'

    @classmethod
    def setUpClass(cls):
        import os
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
        super().setUpClass()

    def setUp(self):
        settings.DEBUG = True
        self.factory = RequestFactory()


    def tearDown(self):
        pass
