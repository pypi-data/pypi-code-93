# -*- coding=utf-8 -*-

from x_py_libs.helpers import UtilitiesHelper


class ModelTransferService(object):
    # keys_relation = None
    # obj = None

    def __init__(self, obj):
        # self.keys_relation = []
        self.obj = obj

    # def transfer_to_py(self, data):
    #     # model = dict(map(lambda x: (x[1], '' if data.get(x[0]) is None else data[x[0]]), self.keys_relation))
    #     for key in self.keys_relation:
    #         ts_attr = key[0]
    #         d = data.get(ts_attr)
    #         setattr(self.obj, key[1], d)

    #     return self.obj

    def auto_transfer(self, data):
        keys = list(data.keys())
        for key in keys:
            snake_key = UtilitiesHelper.camel_2_snake(key)
            # print(key, snake_key)
            setattr(self.obj, snake_key, data.get(key))
        return self.obj
