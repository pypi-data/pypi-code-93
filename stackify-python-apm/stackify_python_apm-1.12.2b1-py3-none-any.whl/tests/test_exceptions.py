from unittest import TestCase

from stackifyapm.exceptions import StackifyAPMException


class StackifyAPMExceptionTest(TestCase):

    def test_exception(self):
        e = StackifyAPMException("Manual Exception")

        assert str(e) == "Manual Exception"
        assert isinstance(e, StackifyAPMException)
        assert isinstance(e, Exception)
