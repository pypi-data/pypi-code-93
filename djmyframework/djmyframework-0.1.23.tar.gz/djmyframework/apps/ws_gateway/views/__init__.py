# -*- coding: utf-8 -*-

from django.contrib import messages

from framework.route import Route
from framework.views import api_get, notauth, render_to_response
from myadmin.models import User


@Route()
@notauth
@api_get()
def test(request):
    messages.info(request, 'test messages')
    #users = list(User.objects.all())
    #print(users)
    return render_to_response('ws_gateway/test.html', locals())


@Route()
@notauth
@api_get()
def js(request):
    return render_to_response('ws_gateway/ws.js', locals(), content_type='application/javascript')
