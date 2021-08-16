# -*- coding: utf-8 -*-
# @Time    : 2020-07-07 15:43
# @Author  : xzr
# @File    : settings
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    :

import os
from settings import BASE_DIR

SVN_ROOT = '%s/svn' % BASE_DIR

# 对应  svnserve.conf  password-db 文件路径
SVN_PASSWORD_DB_FILE = os.path.join(SVN_ROOT, 'conf', 'password.ini')
# 对应  svnserve.conf authz-db 文件路径
SVN_AUTH_DB_FILE = os.path.join(SVN_ROOT, 'conf', 'authz.ini')
SVN_GROUP_DB_FILE = os.path.join(SVN_ROOT, 'conf', 'groups.ini')
