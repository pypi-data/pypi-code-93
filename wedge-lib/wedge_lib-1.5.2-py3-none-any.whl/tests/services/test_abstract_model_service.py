from w.django.tests.django_testcase import DjangoTestCase
from w.tests.fixtures.datasets.django_app import models
from w.tests.fixtures.datasets.services.model_services import ExampleService


class TestAbstractModelService(DjangoTestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    """
    create
    """

    def test_create_with_success_return_instance(self):
        """ Ensure create succeed """
        actual = ExampleService.create(attribute_one="one", attribute_two="two")
        assert isinstance(actual, models.Example)
        assert actual.attribute_one == "one"
        assert actual.attribute_two == "two"

    # todofsc: finir les tests
