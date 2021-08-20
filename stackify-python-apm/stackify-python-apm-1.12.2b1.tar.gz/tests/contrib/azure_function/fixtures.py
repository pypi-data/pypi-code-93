import requests

from stackifyapm.contrib.azure_function import HandlerWrapper


@HandlerWrapper()
def test_azure_function(req):
    pass


@HandlerWrapper()
def test_azure_function_with_context(req, context):
    pass


@HandlerWrapper()
def test_azure_function_with_span(req):
    requests.get('https://www.python.org/')


@HandlerWrapper()
def test_azure_function_with_exception(req):
    raise Exception('test_error')


OPTIONS = {
    'application_name': 'test_name',
    'environment': 'test',
}


@HandlerWrapper(**OPTIONS)
def test_azure_function_with_options(req):
    pass
