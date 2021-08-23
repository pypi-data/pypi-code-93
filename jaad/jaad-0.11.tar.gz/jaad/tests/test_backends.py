from django.forms import BooleanField as DjangoBooleanField
from django.test import SimpleTestCase
from jaad.backends import JaadBackend
from jaad.forms.fields import BooleanField as JaadBooleanField

SIMPLE_DICT = {
    "correspondents": {"from": "user", "to": "world"},
    "messages": ["hello", "everybody"],
}


class RendererTests(SimpleTestCase):
    maxDiff = None

    def test_that_get_field_type_handle_django_fields(self):
        self.assertEqual("string", JaadBackend._get_field_type(DjangoBooleanField()))

    def test_that_get_field_type_handle_field_with_type_override(self):
        self.assertEqual("boolean", JaadBackend._get_field_type(JaadBooleanField()))
