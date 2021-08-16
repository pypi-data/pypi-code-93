# -*- coding: utf-8 -*-
# @Time    : 2020-07-16 15:38
# @Author  : xzr
# @File    : settings
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 

# 是否跟随 django 启动
import os
from framework.settings import settings

LDAP_ACCOUNT_FOLLOW_START = False
# 默认 ldap 服务器 端口
LDAP_ACCOUNT_SERVER_PORT = 3891
DBPATH = os.path.join(settings.PROJECT_ROOT, 'ldiftree.tmp')


from settings import *