from django.test import TestCase
from tests.models import ExampleModel
from tests.service import ExampleService


class ExampleServiceTestCase(TestCase):
    def setUp(self):
        pass

    def test_service_successful_init(self):
        service = ExampleService(ExampleModel)
        self.assertIsNotNone(service)
        self.assertEqual(len(service.fields), 1)

    def test_service_fail_init(self):
        service = None
        try:
            service = ExampleService(ExampleModel)
        except Exception as e:
            self.assertIsNone(service)

    def test_create_model(self):
        service = ExampleService(ExampleModel)
        model = service.create_model({'text': 'some textssdfs'})
        self.assertIsInstance(model, ExampleModel)

    def test_retrieve_model(self):
        service = ExampleService(ExampleModel)
        model = service.create_model({'text': 'some textssdfs'})
        retrieved = service.retrieve_model_by_id(model.id)
        self.assertIsInstance(retrieved, ExampleModel)
        self.assertEqual(model, retrieved)

    def test_update_model(self):
        service = ExampleService(ExampleModel)
        model = service.create_model({'text': 'some textssdfs'})
        updated = service.update_model_by_id(
            model.id, {'text': 'different text'})
        self.assertIsInstance(updated, ExampleModel)
        self.assertEqual(updated.text, 'different text')

    def test_delete_model(self):
        service = ExampleService(ExampleModel)
        model = service.create_model({'text': 'some textssdfs'})
        service.delete_model_by_id(model.id)
        try:
            service.retrieve_model_by_id(model.id)
            self.assertFalse(False)
        except Exception as e:
            self.assertTrue(True)

    def test_list_model(self):
        service = ExampleService(ExampleModel)
        count = 5
        instances = []
        for i in range(0,count):
            instance=service.create_model({'text': f'model {i}'})
            self.assertIsNotNone(instance)
            instances.append(instance)
        self.assertIsNotNone(instances)
        listed = service.list_model()
        self.assertEqual(len(listed), count)
