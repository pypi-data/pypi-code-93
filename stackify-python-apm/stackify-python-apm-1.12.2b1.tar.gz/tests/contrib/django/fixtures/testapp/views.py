from __future__ import absolute_import

import logging

from django.template import RequestContext, Template
from django.http import HttpResponse


def index(request):
    return HttpResponse("")


def exception(request):
    1 // 0
    return HttpResponse("")


def rum(request):
    template = Template('<html><head>{{ stackifyapm_inject_rum | safe }}</head></html>')
    context = RequestContext(request)
    return HttpResponse(template.render(context))


def rum_auto(request):
    template = Template('<html><head></head></html>')
    context = RequestContext(request)
    return HttpResponse(template.render(context))


def test_logging(request):
    logger = logging.getLogger('django_stream')
    logger.level = logging.DEBUG
    logger.info('test info log')
    return HttpResponse("")


# rum_masking/<ip>/<id>/<guid>/<email>/<semicolon>/asdfsdfsdf/<dummy>
def rum_masking(request, ip, id, guid, email, semicolon, dummy=None):
    template = Template('<html><head></head></html>')
    context = RequestContext(request)
    return HttpResponse(template.render(context))
