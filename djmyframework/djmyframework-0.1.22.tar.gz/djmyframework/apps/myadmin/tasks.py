# -*- coding: utf-8 -*-
# @Time    : 2019-09-02 16:02
# @Author  : xzr
# @File    : tasks.py
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 

import time

from django.db import close_old_connections, connections

from config.celery_app import app
from framework.utils.log import log


@app.task(bind=True)
def sayhello(self, a, b):
    log.info(self.name)

    log.info("root")
    time.sleep(2)
    from .models import User

    print(User.objects.all())
    self.update_state(state="PROGRESS", meta={'progress': 50})
    time.sleep(1)
    self.update_state(state="PROGRESS", meta={'progress': 90})
    time.sleep(2)

    #print(connections.databases)
    # CONN_MAX_AGE 不会关闭
    close_old_connections()
    return 'hello world: %s' % a
