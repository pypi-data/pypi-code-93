# -*- coding: utf-8 -*-


class Singleton(type):
    _intcs = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._intcs:
            cls._intcs[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._intcs[cls]
