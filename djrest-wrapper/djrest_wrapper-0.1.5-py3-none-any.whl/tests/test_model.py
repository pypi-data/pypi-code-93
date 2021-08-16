from uuid import UUID
from django.test import TestCase
from tests.models import ExampleModel


class ExampleModelTestCase(TestCase):
    def setUp(self):
        ExampleModel.objects.create(text='some text')

    def test_model_id_field(self):
        for obj in ExampleModel.objects.all():
            self.assertIsInstance(obj.id, UUID)
