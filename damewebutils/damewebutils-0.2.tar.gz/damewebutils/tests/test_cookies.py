#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2019  David Arroyo Menéndez

# Author: David Arroyo Menéndez <davidam@gnu.org>
# Maintainer: David Arroyo Menéndez <davidam@gnu.org>

# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.

# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with damewebutils; see the file LICENSE.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA,


from unittest import TestCase
from http import cookies
import requests


class TestCookies(TestCase):

    def test_cookies(self):
        C = cookies.SimpleCookie()
        C["fig"] = "newton"
        C["sugar"] = "water"
        self.assertEqual(str(C["fig"]), "Set-Cookie: fig=newton")
        self.assertEqual(str(C["sugar"]), "Set-Cookie: sugar=water")
        C["rocky"] = "road"
        C["rocky"]["path"] = "/cookie"
        strcookie1 = "Cookie: fig=newton\r\n"
        strcookie1 = strcookie1 + "Cookie: rocky=road; "
        strcookie1 = strcookie1 + "Path=/cookie\r\nCookie: sugar=water"
        self.assertEqual(str(C.output(header="Cookie:")), strcookie1)
        strcookie2 = 'Cookie: fig=newton\r\nCookie: rocky=road\r\n'
        strcookie2 = strcookie2 + 'Cookie: sugar=water'
        self.assertEqual(str(C.output(attrs=[], header="Cookie:")), strcookie2)

    def test_cookies2(self):
        C = cookies.SimpleCookie()
        # load from a string (HTTP header)
        C.load("chips=ahoy; vienna=finger")
        strcookie = "Set-Cookie: chips=ahoy\r\n"
        strcookie = strcookie + "Set-Cookie: vienna=finger"
        self.assertEqual(str(C), strcookie)

    def test_cookies3(self):
        C = cookies.SimpleCookie()
        C["oreo"] = "doublestuff"
        C["oreo"]["path"] = "/"
        self.assertEqual(str(C), "Set-Cookie: oreo=doublestuff; Path=/")

    def test_cookies4(self):
        C = cookies.SimpleCookie()
        C["twix"] = "none for you"
        self.assertEqual(C["twix"].value, "none for you")

    def test_cookies5(self):
        C = cookies.SimpleCookie()
        # equivalent to C["number"] = str(7)
        C["number"] = 7
        C["string"] = "seven"
        self.assertEqual(C["number"].value, '7')
        self.assertEqual(C["string"].value, "seven")

    def test_session(self):
        s = requests.Session()
        s.get('http://httpbin.org/cookies/set/sessioncookie/123456789')
        r = s.get("http://httpbin.org/cookies")
        str1 = '{\n  "cookies": {\n    '
        str1 = str1 + '"sessioncookie": "123456789"\n  }\n}\n'
        self.assertEqual(r.text, str1)
