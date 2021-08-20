from unittest import TestCase

from stackifyapm.decorators import exception_handler


class MockClass(object):
    def __init__(self):
        self.called = False


@exception_handler(message="Some message")
def no_exception(mock_class):
    mock_class.called = True
    return True


@exception_handler(message="Some message")
def with_exception(mock_class):
    raise Exception("some exception")
    mock_class.called = True
    return True


class ExceptionHandlerTest(TestCase):

    def test_no_exception(self):
        mock_class = MockClass()

        response = no_exception(mock_class)

        assert response is True
        assert mock_class.called is True

    def test_with_exception(self):
        mock_class = MockClass()

        response = with_exception(mock_class)

        assert response is None
        assert mock_class.called is False
