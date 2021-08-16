# -*- coding: utf-8 -*-
# @Time    : 2021-03-25 15:47
# @Author  : xzr
# @File    : test_LDAPSHA1PasswordHasher
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    :
from unittest import TestCase


class TestLDAPSHA1PasswordHasher(TestCase):
    def test_encode(self):

        from ..authentication import LDAPSHA1PasswordHasher

        hasher = LDAPSHA1PasswordHasher()
        source_str = 'asd'
        s = hasher.encode(source_str)
        print()
        print(s)
        print(hasher.verify(source_str,s))
        self.assertTrue(hasher.verify(source_str,s))
        print(hasher.safe_summary(s))
        #self.fail()
