# -*- coding: utf-8 -*-
# @Time : 2020-06-05 16:22
# @Author : xzr
# @File : enum.py
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc :

from framework.utils.myenum import Enum
from .translation import _


class BoolEnum(Enum):
    Yes = 1, _('是')
    No = 0, _('否')


