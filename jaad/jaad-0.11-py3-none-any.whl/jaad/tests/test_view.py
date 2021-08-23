from django.test import SimpleTestCase
from jaad.forms import fields
from jaad.view import JaadView, with_parameters


class SomeParameters(fields.Form):
    name = fields.StringField()
    age = fields.StringField()


class OtherParameters(fields.Form):
    city = fields.StringField()
    country = fields.StringField()


class OtherOtherParameters(fields.Form):
    password = fields.StringField()
    picture = fields.StringField()


class ViewTests(SimpleTestCase):
    maxDiff = None

    def test_that_with_parameters_decorator_add_parameters(self):
        class Index(JaadView):
            @with_parameters("GET", SomeParameters, OtherParameters)
            @with_parameters("POST", OtherOtherParameters)
            def get(self, request, parameters):
                pass

        self.assertEqual(
            Index().get.custom_parameters["get"], (SomeParameters, OtherParameters)
        )
        self.assertEqual(Index().get.custom_parameters["post"], (OtherOtherParameters,))
