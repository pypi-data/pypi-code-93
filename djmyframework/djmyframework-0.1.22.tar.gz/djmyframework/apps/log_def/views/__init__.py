# -*- coding: utf-8 -*-
# @Time    : 2020-06-15 15:55
# @Author  : xzr
# @File    : __init__
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 

from framework.route import Route
from framework.views import HttpResponse, notcheck
from log_def.models import DictDefine
from framework.utils import json_dumps


@Route('^log/dict/interface')
@notcheck
def interface(request):
    """
    兼容旧接口
    :param request:
    :return:
    """
    key = request.GET.get('key')
    _r = {}
    if key:
        o = DictDefine.objects.filter(key=key).first()
        if o:
            _r = o.get_dict()
    return HttpResponse(json_dumps(_r))
