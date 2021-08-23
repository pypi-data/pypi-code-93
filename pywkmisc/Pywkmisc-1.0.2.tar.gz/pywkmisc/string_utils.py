#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import uuid as _uuid
import time
import random


class StringUtils(object):

    @staticmethod
    def str2md5(string):
        """
        字符串转MD5
        1、参数必须是utf8
        2、python3 所有字符都是unicode形式，已经不存在unicode关键字
        3、python3 str 实质上就是unicode
        """
        if isinstance(string, str):
            # 如果是unicode先转utf-8
            string = string.encode("utf-8")
        m = hashlib.md5()
        m.update(string)
        return m.hexdigest()

    @staticmethod
    def uuid(ns, string, avoid_conflict=True):
        if avoid_conflict:
            data = '{ns}{node}{time}{str}{rand}'.format(
                ns=ns[:12],
                node=_uuid.getnode(),
                time=time.time() * 1000000,
                str=string,
                rand=random.randint(23, 6436343)
            )
        else:
            data = '{ns}{node}{str}'.format(ns=ns[:12], node=_uuid.getnode(), str=string)
        return StringUtils.str2md5(data.encode())

    @staticmethod
    def sha1(string):
        sha1 = hashlib.sha1()
        sha1.update(string)
        return sha1.hexdigest()

    @staticmethod
    def sha512(string):
        sha512 = hashlib.sha512()
        sha512.update(string)
        return sha512.hexdigest()

    @staticmethod
    def empty(string):
        """
        StringUtils.empty(None)      = true
        StringUtils.empty("")        = true
        StringUtils.empty(" ")       = false
        StringUtils.empty("bob")     = false
        StringUtils.empty("  bob  ") = false
        :return:
        """
        return string is None or len(string) == 0

    @staticmethod
    def blank(string):
        """
        StringUtils.blank(None)      = true
        StringUtils.blank("")        = true
        StringUtils.blank(" ")       = true
        StringUtils.blank("bob")     = false
        StringUtils.blank("  bob  ") = false
        :return:
        """
        if string is None or len(string) == 0:
            return True
        return string.isspace()


if __name__ == '__main__':
    pass
