from django.utils.functional import Promise

from django.conf import settings

from django.test import SimpleTestCase
from jaad.exceptions import exception_handler
from rest_framework.exceptions import ValidationError


class RendererTests(SimpleTestCase):
    maxDiff = None

    def test_that_exception_handler_handle_unexpected_exception(self):
        exception = KeyError("Bad key detected")

        handled_exception = self.handle_exception(exception, None, debug_value=False)

        self.assertEqual(
            {
                "status_code": 500,
                "message": "An internal error occurred.",
                "more_info": "Contact the administrator of the application.",
            },
            handled_exception.data,
        )
        self.assertEqual(500, handled_exception.status_code)

    def test_that_exception_handler_handle_expected_exception(self):
        exception = ValidationError(detail="Bad format for the field name")

        response_for_exception = self.handle_exception(
            exception, None, debug_value=False
        )

        self.assertEqual(
            {
                "status_code": 400,
                "message": "Invalid input.",
                "more_info": ["Bad format for the field name"],
            },
            self.get_proxied_value(response_for_exception.data),
        )
        self.assertEqual(400, response_for_exception.status_code)

    def handle_exception(self, exception, context, debug_value):
        previous_debug_value = settings.DEBUG
        settings.DEBUG = debug_value
        returned_value = exception_handler(exception, context)
        settings.DEBUG = previous_debug_value
        return returned_value

    def get_proxied_value(self, some_dict):
        return {
            key: value._proxy____cast() if isinstance(value, Promise) else value
            for key, value in some_dict.items()
        }
