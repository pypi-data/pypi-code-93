# This file is placed in the Public Domain.

import ob
import unittest

from ob.prs import parse_txt

cfg = ob.Default()


class Test_Cfg(unittest.TestCase):
    def test_parse(self):
        parse_txt(cfg, "m=bot.irc")
        self.assertEqual(cfg.sets.m, "bot.irc")

    def test_parse2(self):
        parse_txt(cfg, "m=bot.irc,bot.udp,bot.rss")
        self.assertEqual(cfg.sets.m, "bot.irc,bot.udp,bot.rss")

    def test_edit(self):
        d = {"m": "bot.rss"}
        cfg.edit(d)
        self.assertEqual(cfg.m, "bot.rss")
