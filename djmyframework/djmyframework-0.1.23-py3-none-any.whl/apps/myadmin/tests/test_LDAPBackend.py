# -*- coding: utf-8 -*-
# @Time : 2021-04-05 07:05
# @Author : xzr
# @File : test_LDAPBackend.py
# @Software: PyCharm
# @Contact : xzregg@gmail.com


from . import BaseTestCase
from ..backend.ldap import LDAPBackend


class TestLDAPBackend(BaseTestCase):

    def atest_ldap(self):
        l = LDAPBackend('test1', 'tt')
        u = l.authenticate()
        print(u)

