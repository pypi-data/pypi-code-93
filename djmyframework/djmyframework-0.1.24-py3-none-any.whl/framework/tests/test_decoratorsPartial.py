# -*- coding: utf-8 -*-
# @Time    : 2021-04-09 10:30
# @Author  : xzr
# @File    : test_decoratorsPartial
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    :
from unittest import TestCase
from ..utils import DecoratorsPartial

class TestDecoratorsPartial(TestCase):
    def test_decorators(self):

        def dec1(a1='a1'):
            def decorator(func):
                print((a1))
                return func
            return decorator

        dp = DecoratorsPartial(dec1,'a2')

        @dec1('a1')
        def f1():
            """f1"""
            pass


        @dp
        def f2():pass



        @dp('a3')
        def f3():pass

        @dp()
        def f4(): pass

        f1()
        f2()
        f3()
        f4()