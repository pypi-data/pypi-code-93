# This file is placed in the Public Domain.

import ob
import random
import unittest

events = []
k = ob.krn.kernel()

param = ob.Object()
param.add = ["test@shell", "bart", ""]
param.cfg = ["cfg server=localhost", "cfg", ""]
param.dne = ["test4", ""]
param.rm = ["reddit", ""]
param.dpl = ["reddit title,summary,link", ""]
param.log = ["test1", ""]
param.flt = ["0", ""]
param.fnd = [
    "bot.irc.Cfg",
    "bot.log.Log",
    "bot.tdo.Todo",
    "bot.rss.Rss",
    "bot.irc.Cfg server==localhost",
    "bot.rss.Rss rss==reddit rss",
]
param.rss = ["https://www.reddit.com/r/python/.rss"]
param.tdo = ["test4", ""]


class Test_Threaded(unittest.TestCase):
    def test_thrs(self):
        thrs = []
        for x in range(k.cfg.index or 1):
            thr = ob.launch(exec)
            thrs.append(thr)
        for thr in thrs:
            thr.join()
        consume()


def consume():
    fixed = []
    res = []
    for e in events:
        e.wait()
        fixed.append(e)
    for f in fixed:
        try:
            events.remove(f)
        except ValueError:
            continue
    return res


def exec():
    c = ob.bus.Bus.first()
    l = list(k.cmds)
    random.shuffle(l)
    for cmd in l:
        for ex in getattr(param, cmd, [""]):
            e = c.event(cmd + " " + ex)
            k.dispatch(e)
            events.append(e)
