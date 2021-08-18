# This file is in the Public Domain.

import ob
import threading
import time

k = ob.krn.kernel()
starttime = time.time()


def flt(event):
    try:
        index = int(event.args[0])
        event.reply(ob.fmt(ob.bus.Bus.objs[index], skip=["queue", "ready", "iqueue"]))
        return
    except (TypeError, IndexError):
        pass
    event.reply(" | ".join([ob.thr.getname(o) for o in Bus.objs]))


def thr(event):
    psformat = "%s %s"
    result = []
    for thr in sorted(threading.enumerate(), key=lambda x: x.getName()):
        if str(thr).startswith("<_"):
            continue
        o = ob.Object()
        ob.update(o, vars(thr))
        if ob.get(o, "sleep", None):
            up = o.sleep - int(time.time() - o.state.latest)
        else:
            up = int(time.time() - starttime)
        thrname = thr.getName()
        if not thrname:
            continue
        if thrname:
            result.append((up, thrname))
    res = []
    for up, txt in sorted(result, key=lambda x: x[0]):
        res.append("%s(%s)" % (txt, ob.tms.elapsed(up)))
    if res:
        event.reply(" ".join(res))


def upt(event):
    event.reply("uptime is %s" % ob.tms.elapsed(time.time() - starttime))
