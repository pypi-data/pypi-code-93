# -*- coding: utf-8 -*-
# @Time : 2021-04-10 21:18
# @Author : xzr
# @File : celery_app.py
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc :

from __future__ import absolute_import, unicode_literals

from config.celery_app import app
from celery import Celery, Task
from celery.result import AsyncResult
