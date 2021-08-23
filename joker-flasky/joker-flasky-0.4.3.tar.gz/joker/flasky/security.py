#!/usr/bin/env python3
# coding: utf-8

import hashlib
import time


def _make_salt():
    return hex(int(time.time() * 65555))[-10:][::-1]


class HashedPassword(object):
    def __init__(self, digest: str, algo: str, salt: str):
        self.digest = digest
        self.algo = algo
        self.salt = salt

    @classmethod
    def parse(cls, hp_string: str):
        digest, algo, salt = hp_string.split(':')
        return cls(digest, algo, salt)

    @classmethod
    def generate(cls, password: str, algo: str = 'sha256', salt: str = None):
        if salt is None:
            salt = _make_salt()
        p = password.encode('utf-8')
        s = salt.encode('utf-8')
        h = hashlib.new(algo, p + s)
        return cls(h.hexdigest(), algo, salt)

    def __str__(self):
        return '{}:{}:{}'.format(self.digest, self.algo, self.salt)

    def verify(self, password: str):
        hp1 = self.generate(password, self.algo, self.salt)
        return self.digest == hp1.digest
