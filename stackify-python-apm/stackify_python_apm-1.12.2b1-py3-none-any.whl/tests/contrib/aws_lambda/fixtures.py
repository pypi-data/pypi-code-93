import requests


def test_handler_function(event, context):
    return True


def test_handler_function_with_span(event, context):
    requests.get('https://www.python.org/')


def test_handler_function_with_exception(event, context):
    raise Exception('test_error')
