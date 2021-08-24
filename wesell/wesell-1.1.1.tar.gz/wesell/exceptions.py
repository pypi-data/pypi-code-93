# -*- coding: utf-8 -*-
# python2 / python3 exception 兼容
# 使用:
# from wesell.exceptions import *
from __future__ import absolute_import
import sys

if sys.version_info.major == 2:
    from exceptions import *

