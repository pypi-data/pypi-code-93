# This file is placed in the Public Domain.

import unittest

from obj import Object, edit
from obj.prs import parse_txt

cfg = Object()


class Test_Cfg(unittest.TestCase):
    def test_parse(self):
        parse_txt(cfg, "m=irc")
        self.assertEqual(cfg.sets.m, "irc")

    def test_parse2(self):
        parse_txt(cfg, "m=irc,udp,rss")
        self.assertEqual(cfg.sets.m, "irc,udp,rss")

    def test_edit(self):
        d = Object({"m": "irc,rss,udp"})
        edit(cfg, d)
        self.assertEqual(cfg.m, "irc,rss,udp")
