# -*- coding: utf-8 -*-
# @Time : 2020-04-27 14:17
# @Author : xzr
# @File : context_processors.py
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc :

from .settings import settings


def context_settings(request):
    return {
            'settings': settings
    }
