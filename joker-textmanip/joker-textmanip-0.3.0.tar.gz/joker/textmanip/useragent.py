#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import re
from collections import OrderedDict

import six


class UserAgent(object):
    """
    https://en.wikipedia.org/wiki/User_agent#Format_for_human-operated_web_browsers
    Mozilla/[version] ([system/browser info]) [platform] ([platform details]) [extensions]
    """
    # ci = case insensitive
    __slots = ['_tokens', '_ci_tokens', '_system', '_string']

    def __init__(self, tokens):
        # OrderedDict
        self._tokens = OrderedDict(tokens)
        # plain dict
        self._ci_tokens = {k.lower(): v for (k, v) in self._tokens.items()}
        # self.system = self[next(iter(self._data))]['comment']
        self._system = None
        self._string = None

    @classmethod
    def from_string(cls, string):
        tokens = cls.decompose(string)
        o = cls(tokens)
        if not o._tokens:
            raise ValueError('bad User-Agent format')
        o._string = string
        return o

    @property
    def system(self):
        if self._system is None:
            v = next(six.itervalues(self._tokens))
            if isinstance(v, tuple) and len(v) == 2:
                self._system = v[1]
            else:
                self._system = ''
        return self._system

    @property
    def string(self):
        if not self._string:
            self._string = self.assemble()
        return self._string

    def __repr__(self):
        c = self.__class__.__name__
        return '{}({})'.format(c, list(self._tokens.items()))

    def __str__(self):
        return self.string

    def __getitem__(self, key):
        return self._ci_tokens[key.lower()]

    def __setitem__(self, key, value):
        if not isinstance(value, str):
            value = tuple(value)
        else:
            raise TypeError('value must be str or dict')

        self._tokens[key] = value
        self._ci_tokens[key.lower()] = value
        self._system = None
        self._string = None

    def assemble(self):
        segments = []
        for key, value in six.iteritems(self._tokens):
            if not value:
                seg = key
            elif isinstance(value, str):
                seg = '{}/{}'.format(key, value)
            elif isinstance(value, tuple):
                seg = '{}/{} ({})'.format(key, *value)
            else:
                raise TypeError()
            segments.append(seg)
        return ' '.join(segments)

    def get(self, key, default=None):
        return self._ci_tokens.get(key.lower(), default)

    @staticmethod
    def split(string):
        pattern = r"""
            \s*(        # do NOT capture whitespaces
            \(
            [^()]*      # anything but braces
            \)
            )\s*
        """
        return re.split(pattern, string, flags=re.VERBOSE)

    @staticmethod
    def decompose(string):
        string = string.strip()
        regex = re.compile(r"""
            ([^/()]+)         # no /, no (), no whitespaces
            (?:
                /
                ([^()\s]*)      # /xxxx
            )?
            \s*                 # whitespaces
            (?:
                \(
                ([^()]*)        # anything but braces, allowing whitespaces
                \)
            )?
            \s*
        """, re.VERBOSE)
        # tokens = OrderedDict()
        for name, version, comment in regex.findall(string):
            # if comment:
            #     tokens[t] = (version, comment)
            # else:
            #     tokens[t] = version
            if comment:
                yield name, (version, comment)
            else:
                yield name, version
        # return tokens

    def is_ipad(self):
        # http://artsy.github.io/blog/2012/10/18
        # /the-perils-of-ios-user-agent-sniffing/
        s = self.system.lower()
        return 'ipad' in s

    def is_iphone(self):
        # http://artsy.github.io/blog/2012/10/18
        # /the-perils-of-ios-user-agent-sniffing/
        s = self.system.lower()
        if 'ipad' in s:
            return False
        return 'iphone' in s or 'ipod' in s

    def is_mobile(self):
        # https://developer.mozilla.org/en-US/docs\
        # /web/HTTP/Browser_detection_using_the_user_agent
        return 'Mobi' in self.string

    def is_msie(self):
        return 'msie' in self.system.lower()
