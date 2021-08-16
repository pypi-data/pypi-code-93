# -*- coding: utf-8 -*-
# @Time : 2021-02-08 19:26
# @Author : xzr
# @File : authentication.py
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc :


import base64
import random

from django.contrib.auth.hashers import BasePasswordHasher
from django.utils.encoding import force_bytes
from rest_framework.authentication import SessionAuthentication

try:
    from hashlib import sha1
except ImportError:
    from sha import sha as sha1


class LDAPSHA1PasswordHasher(BasePasswordHasher):
    algorithm = "ssha"
    ident = "{SSHA}"
    checksum_size = 20

    def encode(self, password, salt=None):
        # passlib.hash.ldap_salted_sha1.encrypt(password_str)
        assert password is not None

        if salt is None:
            salt = ''
            for i in range(8):
                salt += chr(random.randint(0, 127))
            salt = salt.encode('ascii')
        salt = force_bytes(salt)
        s = sha1()
        s.update(force_bytes(password))
        s.update(salt)
        encoded = base64.encodebytes(s.digest() + salt).rstrip()
        return "%s$%s" % (self.algorithm, encoded.decode('ascii'))

    def verify(self, password, encoded):
        algorithm, raw = encoded.split('$', 1)
        raw = base64.decodebytes(raw.encode())
        salt = raw[self.checksum_size:]
        got = self.encode(password, salt)
        return encoded == got

    def safe_summary(self, encoded: str):
        algorithm, raw = encoded.split('$', 1)
        assert algorithm == self.algorithm
        return {
                'algorithm': algorithm,
                'salt'     : raw[self.checksum_size:],
                'hash'     : raw[:self.checksum_size]
        }


class MySessionAuthentication(SessionAuthentication):
    def authenticate(self, request):
        user = getattr(request._request, 'user', None)

        if not user :
            return None

        return (user, None)
