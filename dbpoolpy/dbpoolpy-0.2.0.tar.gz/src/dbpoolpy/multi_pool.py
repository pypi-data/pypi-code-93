#!/usr/bin/env python
# -*- coding: utf-8 -*-

class MultiPool(object):
    def __init__(self, pool_dict=None):
        self.pool_dict = pool_dict or dict()
    
    def __len__(self):
        return len(self.pool_dict)
    
    def __getitem__(self, key):
        return self.pool_dict[key]
    
    def __setitem__(self, key, value):
        self.pool_dict[key] = value

    def __delitem__(self, key):
        del self.pool_dict[key]

    def __iter__(self):
        return iter(list(self.pool_dict.values()))

    def __bool__(self):
        return bool(self.pool_dict)

    def update(self, multi_pool):
        self.pool_dict.update(multi_pool)

    def keys(self):
        return list(self.pool_dict.keys())

    def values(self):
        return list(self.pool_dict.values())
    
    def items(self):
        return list(self.pool_dict.items())

    def get(self, key):
        return self.pool_dict.get(key)

