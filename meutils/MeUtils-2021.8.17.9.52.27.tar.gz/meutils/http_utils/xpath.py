#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : xpath
# @Time         : 2021/3/22 11:48 上午
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : 



from lxml.etree import HTML
from meutils.http_utils import request



r = request()
dom_tree = HTML(r.text)
dom_tree.xpath('//*[@id="sogou_vr_11002601_box_0"]/div[2]')

