# -*- coding: utf-8 -*-
# @Time    : 2021-03-16 11:00
# @Author  : xzr
# @File    : renderers
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 

from rest_framework.renderers import JSONRenderer as RestJSONRenderer

from .utils import MyJsonEncoder


class JSONRenderer(RestJSONRenderer):
    encoder_class = MyJsonEncoder


class DebugRenderer(JSONRenderer):
    format = 'debug'

    media_type = 'text/html'

    def render(self, *args, **kwargs):
        rsp = super().render( *args, **kwargs)
        return b'<body>%s</body>' % rsp
