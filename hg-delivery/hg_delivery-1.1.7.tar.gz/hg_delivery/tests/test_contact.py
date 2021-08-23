import unittest
from pyramid import testing

# ------------------------------------------------------------------------------


class Contact(unittest.TestCase):

    def test_simple_request(self):
        """
            test dummy view
        """
        from ..views import contact
        request = testing.DummyRequest()
        result = contact(request)
        self.assertEqual(len(result), 0)
        self.assertIsInstance(result, dict)
