#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : gensim
# @Time         : 2021/4/6 3:29 下午
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  :

import gensim


class ANN(object):

    def __init__(self, vector_size=768):
        self.model = gensim.models.KeyedVectors(vector_size)

    def add_vec(self, entities, weights, replace=False):
        self.model.add(entities, weights, replace)
        self.model.init_sims(replace=True)  # 省内存
        return self
