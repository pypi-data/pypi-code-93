# -*- coding: utf-8 -*-
# @Time    : 2021-04-14 11:16
# @Author  : xzr
# @File    : test_settingOptions
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    :

from unittest import TestCase
from framework.utils.log import logger

class TestSettingOptions(TestCase):

    def test_cls(self):
        class Parent(object):
            def __new__(cls, value, *args, **kwargs):
                if kwargs.pop('is_new', True):
                    _t = type(value)
                    clazz = type('cc', (cls,_t), {})
                    kwargs['is_new'] = False
                    self = clazz.__new__(clazz, value, *args, **kwargs)
                    return self
                else:
                    return super().__new__(cls, value)

            def __init__(self, value=1, b=2, c=3, d=4):
                self.p = 1
                self.value= value
                self.type=type(value)
                self.b = b
                self.c = c
                self.d = d
                self.__type= type(value)
            def __bool__(self):
                return bool(self.a)

            def __get__(self, name):
                return super().__get__(name)
            def __getattr__(self, name):
                return super().__getattribute__(name)

            def __getattribute__(self, item):

                return super().__getattribute__(item)

            def pp(self):
                print('pp')
                return self.p

        class A(str, Parent):
            def f1(self):
                return 'f1'

        # B=type('cc',(Parent,int),{})

        a = Parent('a', 2, 3, 4)
        a.a = 'asdasd'

        b = Parent(1, 2, 3, 4)
        c = Parent([3,4], 2, 3, 4)
        d = Parent({2:3}, 2, 3, 4)
        e = Parent(set([2,3,4]), 2, 3, 4)
        a.lower()
        if a:
            print(3)
        logger.info(type(a))
        logger.info(isinstance(a, int))
        logger.info(a.p)
        logger.info(a.pp())
        self.assertTrue(isinstance(a,str))
        self.assertTrue(isinstance(b, int))
        self.assertTrue(isinstance(d, dict))
